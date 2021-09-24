import random

import arcade
from pyglet.math import Vec2  # type: ignore

from pw32n import geography, sprite_images, models, tiles, enemy_sprites

SCREEN_TITLE = "pyweek32-neverending"


class GameWindow(arcade.Window):
    def __init__(self) -> None:
        self.geo: geography.Geography[tiles.Tile] = geography.Geography()
        super().__init__(
            self.geo.screen_width, self.geo.screen_height, SCREEN_TITLE, resizable=True
        )
        self.player_model = models.PlayerModel()
        self.set_min_size(self.geo.min_screen_width, self.geo.min_screen_height)
        self.show_view(WorldView())

    def on_resize(self, width: float, height: float) -> None:
        width = int(width)
        height = int(height)
        super().on_resize(width, height)
        self.geo.screen_width = width
        self.geo.screen_height = height


class WorldView(arcade.View):
    PLAYER_MOVEMENT_SPEED = 5

    # This matches the grassy tile.
    BACKGROUND_COLOR = (57, 194, 114)

    # How fast the camera pans to the player. 1.0 is instant.
    CAMERA_SPEED = 1.0

    def __init__(self) -> None:
        super().__init__()
        self.geo = self.window.geo
        self.sprite_map: dict[geography.OriginPoint, arcade.Sprite] = {}
        self.player_list = arcade.SpriteList()
        self.enemy_sprite_list = arcade.SpriteList()
        self.walkable_tiles_sprite_list = arcade.SpriteList()
        self.unwalkable_tiles_sprite_list = arcade.SpriteList()

        # These contain all of the sprites that need to shift when the player moves.
        self.world_sprite_lists: list[arcade.SpriteList] = [
            self.walkable_tiles_sprite_list,
            self.unwalkable_tiles_sprite_list,
            self.enemy_sprite_list,
        ]

        self.player_sprite = arcade.Sprite(
            sprite_images.PLAYER_IMAGE.filename, sprite_images.PLAYER_IMAGE.scaling
        )

        # Even though we show the player in the middle of the screen, he really lives at the
        # center of the universe, and we move the camera to compensate.
        self.player_sprite.center_x = 0
        self.player_sprite.center_y = 0

        self.player_list.append(self.player_sprite)
        self.camera_sprites = arcade.Camera(self.window.width, self.window.height)
        self.camera_gui = arcade.Camera(self.window.width, self.window.height)

        # This keeps us from walking through walls.
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.unwalkable_tiles_sprite_list
        )

    def on_show(self) -> None:
        arcade.set_background_color(self.BACKGROUND_COLOR)

    def get_tile(self, tile_point: geography.OriginPoint) -> tiles.Tile:
        tile: tiles.Tile = self.geo.tile_map.get(tile_point)
        if tile is None:
            tile = self.pick_new_tile(tile_point)
            self.geo.tile_map.put(tile_point, tile)
        return tile

    def pick_new_tile(self, tile_point: geography.OriginPoint) -> tiles.Tile:
        surrounding_tiles = self.get_surrounding_tiles(tile_point)

        # About 60% of the time, just do the same as one of the neighboring tiles unless there
        # aren't any. This makes the blocks "clumpier".
        if surrounding_tiles and random.randrange(100) < 60:
            tile = random.choice(surrounding_tiles)

        # Otherwise, there's a 1 in 6 chance of picking a box crate.
        elif random.randrange(6) == 0:
            tile = tiles.BOX_CRATE_TILE

        # Otherwise, pick grass.
        else:
            tile = tiles.GRASS_TILE

        # Whenever we're picking a new tile, and we pick grass, that's a good time to possibly
        # put a new enemy on that tile.
        if tile == tiles.GRASS_TILE:
            self.possibly_create_an_enemy(tile_point)

        return tile

    def get_surrounding_tiles(
        self, tile_point: geography.OriginPoint
    ) -> list[tiles.Tile]:
        surrounding_points = self.geo.surrounding_points(tile_point)
        surrounding_tiles = []
        for p in surrounding_points:
            tile = self.geo.tile_map.get(p)
            if tile is not None:
                surrounding_tiles.append(tile)
        return surrounding_tiles

    def possibly_create_an_enemy(self, op: geography.OriginPoint) -> None:
        if random.randrange(150) != 0:
            return
        enemy = enemy_sprites.EnemySprite(sprite_images.SLIME_IMAGE)
        ap: geography.AdventurePoint = self.geo.origin_point_to_adventure_point(op)
        enemy.left = ap.x
        enemy.top = ap.y
        self.enemy_sprite_list.append(enemy)

    def on_draw(self) -> None:
        arcade.start_render()

        self.camera_sprites.use()  # type: ignore
        for i in self.world_sprite_lists:
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
            self.player_sprite.change_y = self.PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.DOWN:
            self.player_sprite.change_y = -self.PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.LEFT:
            self.player_sprite.change_x = -self.PLAYER_MOVEMENT_SPEED
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_x = self.PLAYER_MOVEMENT_SPEED

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

        # Put the player back where he was (at the center of the universe) and instead move the
        # world in the *opposite* direction.
        self.player_sprite.center_x = 0
        self.player_sprite.center_y = 0
        for i in self.world_sprite_lists:
            i.move(-delta_x, -delta_y)

        self.update_tiles()

        # Move the camera so that the player is in the middle of the screen. This should only be
        # necessary the first time around or when the window resizes, but it probably doesn't
        # hurt to leave it here.
        position = Vec2(
            self.player_sprite.center_x - self.window.width // 2,
            self.player_sprite.center_y - self.window.height // 2,
        )
        self.camera_sprites.move_to(position, self.CAMERA_SPEED)

        # Now that we've sort of left everything in a good state, if we hit an enemy, we should
        # switch to BattleView.
        enemy_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.enemy_sprite_list
        )
        if enemy_hit_list:
            self.window.show_view(BattleView())

    def update_tiles(self) -> None:
        """Add and remove tiles as the user "moves" around."""
        prev_tile_points = set(self.sprite_map.keys())
        new_tile_points = set(self.geo.generate_tile_points())
        tile_point_diff = self.geo.diff_tile_points(prev_tile_points, new_tile_points)
        for tile_point in tile_point_diff.removed:
            sprite = self.sprite_map.pop(tile_point)
            sprite.kill()  # type: ignore
        for tile_point in tile_point_diff.added:
            tile = self.get_tile(tile_point)
            sprite = arcade.Sprite(
                tile.sprite_image.filename, tile.sprite_image.scaling
            )
            self.sprite_map[tile_point] = sprite
            tile_adventure_point = self.geo.origin_point_to_adventure_point(tile_point)
            sprite.left = tile_adventure_point.x
            sprite.top = tile_adventure_point.y
            if tile.is_walkable:
                self.walkable_tiles_sprite_list.append(sprite)
            else:
                self.unwalkable_tiles_sprite_list.append(sprite)

    def on_resize(self, width: float, height: float) -> None:
        # There is no superclass method, but this method definitely gets called.
        width = int(width)
        height = int(height)
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)


class BattleView(arcade.View):
    SIDE_MARGIN = 128

    def __init__(self) -> None:
        super().__init__()
        self.geo = self.window.geo

        self.wall_list: arcade.SpriteList = None
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(
            sprite_images.PLAYER_BATTLE_VIEW_IMAGE.filename,
            scale=sprite_images.PLAYER_BATTLE_VIEW_IMAGE.scaling,
        )
        self.player_list.append(self.player_sprite)

        self.enemy_sprite = arcade.Sprite(
            sprite_images.SLIME_BATTLE_VIEW_IMAGE.filename,
            scale=sprite_images.PLAYER_BATTLE_VIEW_IMAGE.scaling,
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

        self.player_sprite.left = self.SIDE_MARGIN
        self.player_sprite.bottom = self.geo.tile_height
        self.enemy_sprite.right = self.window.width - self.SIDE_MARGIN
        self.enemy_sprite.bottom = self.geo.tile_height

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
