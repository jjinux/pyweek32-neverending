#!/usr/bin/env python3.9

import random
import sys
from typing import NamedTuple

import arcade
from pw32n import geometry
from pyglet.math import Vec2

MIN_PYTHON_VERSION = (3, 9)
SCREEN_TITLE = "Sprite Move with Scrolling Screen Example"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 220

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 1.0

# How fast the character moves
PLAYER_MOVEMENT_SPEED = 5


class TileDetails(NamedTuple):
    filename: str
    scaling: float


PLAYER_TILE = TileDetails(
    ":resources:images/animated_characters/female_person/femalePerson_idle.png",
    scaling=0.4,
)
GRASS_TILE = TileDetails(":resources:images/topdown_tanks/tileGrass2.png", scaling=1.0)
BOX_CRATE_TILE = TileDetails(":resources:images/tiles/boxCrate_double.png", scaling=0.5)


class MyGame(arcade.Window):
    """Main application class."""

    def __init__(self):

        # I need this first since it has screen_width and screen_height.
        self.geo = geometry.Geometry()

        super().__init__(
            self.geo.screen_width, self.geo.screen_height, SCREEN_TITLE, resizable=True
        )

        self.pos_from_origin_x = None
        self.pos_from_origin_y = None

        # Sprite lists
        self.player_list = None
        self.grass_list = None
        self.wall_list = None
        self.map_lists = None

        # Set up the player
        self.player_sprite = None

        # Physics engine so we don't run into walls.
        self.physics_engine = None

        # Create the cameras. One for the GUI, one for the sprites.
        # We scroll the 'sprite world' but not the GUI.
        self.camera_sprites = arcade.Camera(
            self.geo.screen_width, self.geo.screen_height
        )
        self.camera_gui = arcade.Camera(self.geo.screen_width, self.geo.screen_height)

    def setup(self):
        """Set up the game and initialize the variables."""

        self.set_min_size(self.geo.min_screen_width, self.geo.min_screen_height)

        self.pos_from_origin_x = 0
        self.pos_from_origin_y = 0

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.grass_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.map_lists = [self.grass_list, self.wall_list]

        # Set up the player
        self.player_sprite = arcade.Sprite(PLAYER_TILE.filename, PLAYER_TILE.scaling)
        self.player_sprite.center_x = self.geo.initial_position.x
        self.player_sprite.center_y = self.geo.initial_position.y
        self.player_list.append(self.player_sprite)

        # Set up several columns of walls and grass.
        for x in range(200, 1650, 210):
            for y in range(0, 1600, 64):
                tile = self.pick_tile()
                sprite = arcade.Sprite(tile.filename, tile.scaling)
                sprite.center_x = x
                sprite.center_y = y
                if tile == GRASS_TILE:
                    self.grass_list.append(sprite)
                elif tile == BOX_CRATE_TILE:
                    self.wall_list.append(sprite)
                else:
                    raise ValueError(f"Unexpected tile: {tile}")

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.wall_list
        )

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def pick_tile(self):
        if random.randrange(5) == 0:
            return GRASS_TILE
        else:
            return BOX_CRATE_TILE

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw all the sprites.
        for map_list in self.map_lists:
            map_list.draw()
        self.player_list.draw()

        # Select the (unscrolled) camera for our GUI
        self.camera_gui.use()

        # Draw the GUI
        arcade.draw_rectangle_filled(
            self.width // 2, 20, self.width, 40, arcade.color.ALMOND
        )
        text = f"({self.pos_from_origin_x}, {self.pos_from_origin_y})"
        arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """Movement and game logic"""

        prev_player_sprite_center_x = self.player_sprite.center_x
        prev_player_sprite_center_y = self.player_sprite.center_y

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

        delta_x = self.player_sprite.center_x - prev_player_sprite_center_x
        delta_y = self.player_sprite.center_y - prev_player_sprite_center_y

        self.pos_from_origin_x = round(self.pos_from_origin_x + delta_x)
        self.pos_from_origin_y = round(self.pos_from_origin_y + delta_y)

        # Put the player back where he was and instead move the map in the *opposite* direction.
        self.player_sprite.center_x = self.geo.initial_position.x
        self.player_sprite.center_y = self.geo.initial_position.y
        for map_list in self.map_lists:
            map_list.move(-delta_x, -delta_y)

        print("Position from origin:", (self.pos_from_origin_x, self.pos_from_origin_y))
        print("    Moved: ", (delta_x, delta_y))

        for map_list in self.map_lists:
            map_list.draw()
        self.player_list.draw()

        # Move the camera so that the player is in the middle. This should only be necessary the
        # first time around or when the window resizes, but it probably doesn't hurt to leave it here.
        position = Vec2(
            self.player_sprite.center_x - self.width / 2,
            self.player_sprite.center_y - self.height / 2,
        )
        self.camera_sprites.move_to(position, CAMERA_SPEED)

    def on_resize(self, width, height):
        """
        Resize window
        Handle the user grabbing the edge and resizing the window.
        """
        width = int(width)
        height = int(height)
        self.geo.screen_width = width
        self.geo.screen_height = height
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)


def main():
    if sys.version_info[:2] < MIN_PYTHON_VERSION:
        sys.exit(f"This game requires Python {'.'.join(map(str, MIN_PYTHON_VERSION))}")

    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
