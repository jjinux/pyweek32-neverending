import random

import arcade
from pyglet.math import Vec2  # type: ignore

from pw32n import geography, sprite_images, player_model

SCREEN_TITLE = "pyweek32-neverending"
PLAYER_MOVEMENT_SPEED = 5
BATTLE_VIEW_GROUND_HEIGHT = 64
BATTLE_VIEW_SIDE_MARGIN = 128

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 1.0


class GameWindow(arcade.Window):
    def __init__(self) -> None:
        self.geo = geography.Geography()
        super().__init__(
            self.geo.screen_width, self.geo.screen_height, SCREEN_TITLE, resizable=True
        )
        self.player_model = player_model.PlayerModel()
        self.set_min_size(self.geo.min_screen_width, self.geo.min_screen_height)
        self.show_view(WorldView())

    def on_resize(self, width: float, height: float) -> None:
        width = int(width)
        height = int(height)
        super().on_resize(width, height)
        self.geo.screen_width = width
        self.geo.screen_height = height


class WorldView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.geo = self.window.geo
        self.spriteMap: dict[geography.OriginPoint, arcade.Sprite] = {}
        self.player_list = arcade.SpriteList()
        self.grass_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.tile_sprite_lists: list[arcade.SpriteList] = [
            self.grass_list,
            self.wall_list,
        ]
        self.player_sprite = arcade.Sprite(
            sprite_images.PLAYER_IMAGE.filename, sprite_images.PLAYER_IMAGE.scaling
        )
        self.player_sprite.center_x = 0
        self.player_sprite.center_y = 0
        self.player_list.append(self.player_sprite)
        self.camera_sprites = arcade.Camera(self.window.width, self.window.height)
        self.camera_gui = arcade.Camera(self.window.width, self.window.height)

        # This keeps us from walking through walls.
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.wall_list
        )

    def on_show(self) -> None:
        arcade.set_background_color(arcade.color.AMAZON)

    def pick_tile(self) -> sprite_images.SpriteImage:
        if random.randrange(5) == 0:
            return sprite_images.BOX_CRATE_TILE_IMAGE
        else:
            return sprite_images.GRASS_TILE_IMAGE

    def on_draw(self) -> None:
        arcade.start_render()

        self.camera_sprites.use()  # type: ignore
        for i in self.tile_sprite_lists:
            i.draw()
        self.player_list.draw()

        self.camera_gui.use()  # type: ignore
        arcade.draw_rectangle_filled(
            center_x=self.window.width // 2,
            center_y=20,
            width=self.window.width,
            height=40,
            color=arcade.color.ALMOND,
        )
        text = f"Pos: ({self.geo.position.x}, {self.geo.position.y}) Strength: {self.window.player_model.strength:.1f}"
        arcade.draw_text(
            text=text,
            start_x=10,
            start_y=10,
            color=arcade.color.BLACK_BEAN,
            font_size=20,
        )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.ESCAPE:
            self.window.show_view(BattleView())

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.UP or symbol == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif symbol == arcade.key.LEFT or symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time: float) -> None:
        prev_player_sprite_center_x = self.player_sprite.center_x
        prev_player_sprite_center_y = self.player_sprite.center_y

        # This may move the player_sprite.
        self.physics_engine.update()  # type: ignore

        delta_x = round(self.player_sprite.center_x - prev_player_sprite_center_x)
        delta_y = round(self.player_sprite.center_y - prev_player_sprite_center_y)

        self.geo.position = geography.OriginPoint(
            self.geo.position.x + delta_x, self.geo.position.y + delta_y
        )

        self.window.player_model.strength += (abs(delta_x) + abs(delta_y)) * 0.001

        # Put the player back where he was and instead move the world in the *opposite* direction.
        self.player_sprite.center_x = self.geo.initial_position.x
        self.player_sprite.center_y = self.geo.initial_position.y
        for i in self.tile_sprite_lists:
            i.move(-delta_x, -delta_y)

        self.update_tiles()

        for i in self.tile_sprite_lists:
            i.draw()
        self.player_list.draw()

        # Move the camera so that the player is in the middle. This should only be necessary the
        # first time around or when the window resizes, but it probably doesn't hurt to leave it
        # here.
        position = Vec2(
            self.player_sprite.center_x - self.window.width // 2,
            self.player_sprite.center_y - self.window.height // 2,
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
            if tile == sprite_images.GRASS_TILE_IMAGE:
                self.grass_list.append(sprite)
            elif tile == sprite_images.BOX_CRATE_TILE_IMAGE:
                self.wall_list.append(sprite)
            else:
                raise ValueError(f"Unexpected tile: {tile}")

    def on_resize(self, width: float, height: float) -> None:
        # There is no superclass method, but this method definitely gets called.
        width = int(width)
        height = int(height)
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)


class BattleView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.geo = self.window.geo

        self.wall_list: arcade.SpriteList = None
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(
            sprite_images.PLAYER_SIDE_VIEW_IMAGE.filename,
            scale=sprite_images.PLAYER_SIDE_VIEW_IMAGE.scaling,
        )
        self.player_list.append(self.player_sprite)

        self.enemy_sprite = arcade.Sprite(
            sprite_images.SLIME_SIDE_VIEW_IMAGE.filename,
            scale=sprite_images.PLAYER_SIDE_VIEW_IMAGE.scaling,
        )
        self.enemy_list.append(self.enemy_sprite)

        self.update_layout()

    def update_layout(self) -> None:
        # Just throw away the wall_list and start over.
        self.wall_list = arcade.SpriteList()
        for x in range(0, self.window.width, self.geo.tile_width):
            wall = arcade.Sprite(
                sprite_images.GRASS_SIDE_VIEW_TILE_IMAGE.filename,
                sprite_images.GRASS_SIDE_VIEW_TILE_IMAGE.scaling,
            )
            wall.left = x
            wall.bottom = 0
            self.wall_list.append(wall)

        self.player_sprite.left = BATTLE_VIEW_SIDE_MARGIN
        self.player_sprite.bottom = BATTLE_VIEW_GROUND_HEIGHT
        self.enemy_sprite.right = self.window.width - BATTLE_VIEW_SIDE_MARGIN
        self.enemy_sprite.bottom = BATTLE_VIEW_GROUND_HEIGHT

    def on_show(self) -> None:
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self) -> None:
        arcade.start_render()
        self.wall_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(WorldView())

    def on_resize(self, width: float, height: float) -> None:
        # There is no superclass method, but this method definitely gets called.
        self.update_layout()


def main() -> None:
    GameWindow()
    arcade.run()  # type: ignore
