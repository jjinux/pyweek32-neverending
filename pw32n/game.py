import random

import arcade
from pyglet.math import Vec2  # type: ignore

from pw32n import geometry, tiles

SCREEN_TITLE = "Sprite Move with Scrolling Screen Example"

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 1.0

# How fast the character moves
PLAYER_MOVEMENT_SPEED = 5


class MyGame(arcade.Window):
    """Main application class."""

    def __init__(self) -> None:

        # I need this first since it has screen_width and screen_height.
        self.geo = geometry.Geometry()

        super().__init__(
            self.geo.screen_width, self.geo.screen_height, SCREEN_TITLE, resizable=True
        )

        self.spriteMap: dict[geometry.OriginPoint, arcade.Sprite] = None

        # Sprite lists
        self.player_list: arcade.SpriteList = None
        self.grass_list: arcade.SpriteList = None
        self.wall_list: arcade.SpriteList = None
        self.map_lists: list[arcade.SpriteList] = None

        # Set up the player
        self.player_sprite: arcade.Sprite = None

        # Physics engine so we don't run into walls.
        self.physics_engine: arcade.PhysicsEngineSimple = None

        # Create the cameras. One for the GUI, one for the sprites.
        # We scroll the 'sprite world' but not the GUI.
        self.camera_sprites = arcade.Camera(
            self.geo.screen_width, self.geo.screen_height
        )
        self.camera_gui = arcade.Camera(self.geo.screen_width, self.geo.screen_height)

    def setup(self) -> None:
        """Set up the game and initialize the variables."""

        self.set_min_size(self.geo.min_screen_width, self.geo.min_screen_height)
        self.geo.position = self.geo.initial_position
        self.spriteMap = {}

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.grass_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.map_lists = [self.grass_list, self.wall_list]

        # Set up the player
        self.player_sprite = arcade.Sprite(
            tiles.PLAYER_TILE.filename, tiles.PLAYER_TILE.scaling
        )
        self.player_sprite.center_x = self.geo.initial_position.x
        self.player_sprite.center_y = self.geo.initial_position.y
        self.player_list.append(self.player_sprite)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.wall_list
        )

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def pick_tile(self) -> tiles.TileDetails:
        if random.randrange(5) == 0:
            return tiles.BOX_CRATE_TILE
        else:
            return tiles.GRASS_TILE

    def on_draw(self) -> None:
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()  # type: ignore

        # Draw all the sprites.
        for map_list in self.map_lists:
            map_list.draw()
        self.player_list.draw()

        # Select the (unscrolled) camera for our GUI
        self.camera_gui.use()  # type: ignore

        # Draw the GUI
        arcade.draw_rectangle_filled(
            self.width // 2, 20, self.width, 40, arcade.color.ALMOND
        )
        text = f"({self.geo.position.x}, {self.geo.position.y})"
        arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called whenever a key is pressed."""

        if symbol == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the user releases a key."""

        if symbol == arcade.key.UP or symbol == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif symbol == arcade.key.LEFT or symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time: float) -> None:
        """Movement and game logic"""

        prev_player_sprite_center_x = self.player_sprite.center_x
        prev_player_sprite_center_y = self.player_sprite.center_y

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()  # type: ignore

        delta_x = round(self.player_sprite.center_x - prev_player_sprite_center_x)
        delta_y = round(self.player_sprite.center_y - prev_player_sprite_center_y)

        self.geo.position = geometry.OriginPoint(
            self.geo.position.x + delta_x, self.geo.position.y + delta_y
        )

        # Put the player back where he was and instead move the map in the *opposite* direction.
        self.player_sprite.center_x = self.geo.initial_position.x
        self.player_sprite.center_y = self.geo.initial_position.y
        for map_list in self.map_lists:
            map_list.move(-delta_x, -delta_y)

        self.update_tiles()

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

    def update_tiles(self) -> None:
        """Add and remove tiles as the user "moves" around."""
        prev_tile_points = set(self.spriteMap.keys())
        new_tile_points = set(self.geo.generate_tile_points())
        tile_point_diff = self.geo.diff_tile_points(prev_tile_points, new_tile_points)
        for tile_point in tile_point_diff.removed:
            sprite = self.spriteMap.pop(tile_point)
            sprite.kill()  # type: ignore
        for tile_point in tile_point_diff.added:
            tile = self.pick_tile()
            sprite = arcade.Sprite(tile.filename, tile.scaling)
            self.spriteMap[tile_point] = sprite
            tile_adventure_point = self.geo.origin_point_to_adventure_point(tile_point)
            sprite.left = tile_adventure_point.x
            sprite.top = tile_adventure_point.y
            if tile == tiles.GRASS_TILE:
                self.grass_list.append(sprite)
            elif tile == tiles.BOX_CRATE_TILE:
                self.wall_list.append(sprite)
            else:
                raise ValueError(f"Unexpected tile: {tile}")

    def on_resize(self, width: float, height: float) -> None:
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


def main() -> None:
    window = MyGame()
    window.setup()
    arcade.run()  # type: ignore
