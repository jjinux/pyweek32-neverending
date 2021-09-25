import random

import arcade
from pyglet.math import Vec2  # type: ignore

from pw32n import geography, sprite_images, models, tiles, enemy_sprites, battle_moves

SCREEN_TITLE = "Lil Miss Vampire"


class GameWindow(arcade.Window):
    STATUS_HEIGHT = 40

    def __init__(self) -> None:
        self.geo: geography.Geography[tiles.Tile] = geography.Geography()
        super().__init__(
            self.geo.screen_width, self.geo.screen_height, SCREEN_TITLE, resizable=True
        )

        # The models exist "outside" of the sprites because we have two different
        # views interacting with the same models.
        self.player_model = models.PlayerModel()
        self.enemy_models: set[models.EnemyModel] = set()

        self.set_min_size(self.geo.min_screen_width, self.geo.min_screen_height)
        self.show_view(WorldView())

    def on_resize(self, width: float, height: float) -> None:
        width = int(width)
        height = int(height)
        super().on_resize(width, height)
        self.geo.screen_width = width
        self.geo.screen_height = height

    def on_enemy_died(self, enemy: models.EnemyModel) -> None:
        self.enemy_models.remove(enemy)

    def draw_status_at_bottom(self, status: str) -> None:
        """This is a helper function for the different views to have a similar status field at the bottom."""
        arcade.draw_rectangle_filled(
            center_x=self.width // 2,
            center_y=self.STATUS_HEIGHT // 2,
            width=self.width,
            height=self.STATUS_HEIGHT,
            color=arcade.color.ALMOND,
        )
        arcade.draw_text(
            text=status,
            start_x=10,
            start_y=10,
            color=arcade.color.BLACK_BEAN,
            font_size=20,
        )

    def format_strength(self, strength: float) -> str:
        return f"{strength:.1f}"


class WorldView(arcade.View):
    PLAYER_MOVEMENT_SPEED = 5

    # This matches the grassy tile.
    BACKGROUND_COLOR = (57, 194, 114)

    # How fast the camera pans to the player. 1.0 is instant.
    CAMERA_SPEED = 1.0

    # How many screen widths or heights can an enemy be away before it gets killed?
    ENEMY_DISTANCE_KEEPALIVE_RATIO = 3

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
            sprite_images.PLAYER_IMAGE.filename,
            scale=(self.geo.tile_width / sprite_images.PLAYER_IMAGE.width),
        )

        # Even though we show the player in the middle of the screen, he really lives at the
        # center of the universe, and we move the camera to compensate.
        self.player_sprite.center_x = 0
        self.player_sprite.center_y = 0

        self.player_list.append(self.player_sprite)

        for enemy_model in self.window.enemy_models:
            self.create_enemy_sprite_from_model(enemy_model)

        self.update_tiles(initial=True)

        self.camera_sprites = arcade.Camera(self.window.width, self.window.height)
        self.camera_gui = arcade.Camera(self.window.width, self.window.height)

        # This keeps us from walking through walls.
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.unwalkable_tiles_sprite_list
        )

    def on_show(self) -> None:
        arcade.set_background_color(self.BACKGROUND_COLOR)

    def get_tile(
        self, tile_point: geography.OriginPoint, initial: bool = False
    ) -> tiles.Tile:
        tile: tiles.Tile = self.geo.tile_map.get(tile_point)
        if tile is None:
            tile = self.pick_new_tile(tile_point)
            self.geo.tile_map.put(tile_point, tile)

        # If we're calling get_tile, it's because we're walking in a certain direction and loading
        # tiles (pre-existing or not). If the tile is walkable, it's a good time to possibly put
        # a new enemy on that tile.
        #
        # Don't do it when we're initially loading the view. First of all, it's okay if the user
        # has to walk to see their first enemy. Secondly, if I don't do this, then it creates
        # new enemies when I leave the BattleView.
        if tile.is_walkable and not initial:
            self.possibly_create_an_enemy(tile_point)

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
        enemy_strength = models.pick_enemy_strength(op)

        # Just pick a random image for the enemy. For now, all the behavior is the same.
        sprite_image = random.choice(
            (
                sprite_images.ZOMBIE_IMAGE,
                sprite_images.MALE_PERSON_IMAGE,
                sprite_images.FEMALE_PERSON_IMAGE,
                sprite_images.MALE_ADVENTURER_IMAGE,
                sprite_images.ROBOT_IMAGE,
            )
        )

        enemy_model = models.EnemyModel(
            sprite_image=sprite_image,
            position=op,
            strength=enemy_strength,
            player_model=self.window.player_model,
        )
        self.window.enemy_models.add(enemy_model)
        self.create_enemy_sprite_from_model(enemy_model)

    def create_enemy_sprite_from_model(
        self, model: models.EnemyModel
    ) -> enemy_sprites.EnemySprite:
        sprite = enemy_sprites.EnemySprite(
            model,
            model.sprite_image.filename,
            scale=(self.geo.tile_width / model.sprite_image.width),
        )
        ap: geography.AdventurePoint = self.geo.origin_point_to_adventure_point(
            model.position
        )
        sprite.left = ap.x
        sprite.top = ap.y
        self.enemy_sprite_list.append(sprite)
        return sprite

    def on_draw(self) -> None:
        arcade.start_render()

        self.camera_sprites.use()  # type: ignore
        for i in self.world_sprite_lists:
            i.draw()
        self.player_list.draw()

        self.camera_gui.use()  # type: ignore
        status = " ".join(
            [
                f"Pos: ({self.geo.position.x}, {self.geo.position.y})",
                f"Strength: {self.window.format_strength(self.window.player_model.strength)}",
            ]
        )
        self.window.draw_status_at_bottom(status)

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

        self.window.player_model.on_world_view_update(delta_time)

        # Put the player back where he was (at the center of the universe) and instead move the
        # world in the *opposite* direction.
        self.player_sprite.center_x = 0
        self.player_sprite.center_y = 0
        for i in self.world_sprite_lists:
            i.move(-delta_x, -delta_y)

        self.update_enemies()
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
            enemy_model = enemy_hit_list[0].model
            self.window.show_view(BattleView(enemy_model))

    def update_tiles(self, initial: bool = False) -> None:
        """Add and remove tiles as the user "moves" around."""
        prev_tile_points = set(self.sprite_map.keys())
        new_tile_points = set(self.geo.generate_tile_points())
        tile_point_diff = self.geo.diff_tile_points(prev_tile_points, new_tile_points)
        for tile_point in tile_point_diff.removed:
            sprite = self.sprite_map.pop(tile_point)
            sprite.kill()  # type: ignore
        for tile_point in tile_point_diff.added:
            tile = self.get_tile(tile_point, initial=initial)
            sprite = arcade.Sprite(
                tile.sprite_image.filename,
                scale=(self.geo.tile_width / tile.sprite_image.width),
            )
            self.sprite_map[tile_point] = sprite
            tile_adventure_point = self.geo.origin_point_to_adventure_point(tile_point)
            sprite.left = tile_adventure_point.x
            sprite.top = tile_adventure_point.y
            if tile.is_walkable:
                self.walkable_tiles_sprite_list.append(sprite)
            else:
                self.unwalkable_tiles_sprite_list.append(sprite)

    def update_enemies(self) -> None:
        """Throw away enemies that are now too far away from the center of the universe."""
        for enemy_sprite in self.enemy_sprite_list:
            if (
                abs(enemy_sprite.center_x)
                > self.ENEMY_DISTANCE_KEEPALIVE_RATIO * self.window.width
                or abs(enemy_sprite.center_y)
                > self.ENEMY_DISTANCE_KEEPALIVE_RATIO * self.window.height
            ):
                enemy_sprite.kill()
                self.window.on_enemy_died(enemy_sprite.model)

    def on_resize(self, width: float, height: float) -> None:
        # There is no superclass method, but this method definitely gets called.
        width = int(width)
        height = int(height)
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)


class BattleView(arcade.View):
    PLAYER_WIDTH = 128
    SIDE_MARGIN = PLAYER_WIDTH
    MAX_PLAYER_MOVEMENT = PLAYER_WIDTH

    def __init__(self, enemy_model: models.EnemyModel) -> None:
        super().__init__()
        self.geo = self.window.geo
        self.enemy_model = enemy_model

        self.window.player_model.on_battle_view_begin()
        enemy_model.on_battle_view_begin()

        self.wall_list: arcade.SpriteList = None
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite(
            sprite_images.PLAYER_IMAGE.filename,
            scale=(self.PLAYER_WIDTH / sprite_images.PLAYER_IMAGE.width),
        )
        self.player_list.append(self.player_sprite)

        self.enemy_sprite = arcade.Sprite(
            enemy_model.sprite_image.filename,
            scale=(self.PLAYER_WIDTH / enemy_model.sprite_image.width),
        )
        self.enemy_list.append(self.enemy_sprite)

        self.above_status_at_bottom = self.window.STATUS_HEIGHT
        self.above_tiles = self.above_status_at_bottom + self.geo.tile_height
        self.update_background()

    def update_background(self) -> None:
        # Just throw away the wall_list and start over.
        self.wall_list = arcade.SpriteList()
        for x in range(0, self.window.width, self.geo.tile_width):
            wall = arcade.Sprite(
                sprite_images.GRASS_SIDE_VIEW_TILE_IMAGE.filename,
                scale=(
                    self.geo.tile_width / sprite_images.GRASS_SIDE_VIEW_TILE_IMAGE.width
                ),
            )
            wall.left = x
            wall.bottom = self.above_status_at_bottom
            self.wall_list.append(wall)

    def update_combatant_position(
        self,
        model: models.CombatantModel,
        sprite: arcade.Sprite,
        left: int = None,
        right: int = None,
        bottom: int = 0,
    ) -> None:
        delta_x = 0
        delta_y = 0
        rotation = 0.0

        if isinstance(model.state, models.WarmingUpState):
            delta_x = round(
                model.current_battle_move.delta_x
                * model.battle_move_workflow.completion_ratio_for_current_step
                * self.MAX_PLAYER_MOVEMENT
            )
            delta_y = round(
                model.current_battle_move.delta_y
                * model.battle_move_workflow.completion_ratio_for_current_step
                * self.MAX_PLAYER_MOVEMENT
            )
        elif isinstance(model.state, models.ExecutingMoveState):
            delta_x = model.current_battle_move.delta_x * self.MAX_PLAYER_MOVEMENT
            delta_y = model.current_battle_move.delta_y * self.MAX_PLAYER_MOVEMENT
        elif isinstance(model.state, models.CoolingDownState):
            delta_x = round(
                model.current_battle_move.delta_x
                * (1.0 - model.battle_move_workflow.completion_ratio_for_current_step)
                * self.MAX_PLAYER_MOVEMENT
            )
            delta_y = round(
                model.current_battle_move.delta_y
                * (1.0 - model.battle_move_workflow.completion_ratio_for_current_step)
                * self.MAX_PLAYER_MOVEMENT
            )
        elif isinstance(model.state, models.StunnedState):
            rotation = 30.0

        if left is not None:
            sprite.left = left + delta_x
            if rotation != 0:
                sprite.turn_right(rotation)
        elif right is not None:
            sprite.right = right - delta_x
            if rotation != 0:
                sprite.turn_left(rotation)
        sprite.bottom = bottom + delta_y

    def on_show(self) -> None:
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_draw(self) -> None:
        arcade.start_render()
        if self.window.player_model.strength == self.window.player_model.MIN_STRENGTH:
            strength = "Weak"
        else:
            strength = self.window.format_strength(self.window.player_model.strength)
        status = " ".join(
            [
                f"Strength: {strength}",
                f"Enemy: {self.window.format_strength(self.enemy_model.strength)}",
                "(d)odge (j)ab (u)ppercut (esc)ape",
            ]
        )
        self.window.draw_status_at_bottom(status)
        self.wall_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.D:
            self.window.player_model.attempt_battle_move(
                battle_moves.DODGE, self.enemy_model
            )
        elif symbol == arcade.key.J:
            self.window.player_model.attempt_battle_move(
                battle_moves.JAB, self.enemy_model
            )
        elif symbol == arcade.key.U:
            self.window.player_model.attempt_battle_move(
                battle_moves.UPPERCUT, self.enemy_model
            )

        # For now, hitting escape just kills the enemy.
        elif symbol == arcade.key.ESCAPE:
            self.on_enemy_died()

    def on_update(self, delta_time: float) -> None:
        self.window.player_model.on_battle_view_update(delta_time)
        self.enemy_model.on_battle_view_update(delta_time)

        self.update_combatant_position(
            model=self.window.player_model,
            sprite=self.player_sprite,
            left=self.SIDE_MARGIN,
            bottom=self.above_tiles,
        )
        self.update_combatant_position(
            model=self.enemy_model,
            sprite=self.enemy_sprite,
            right=(self.window.width - self.SIDE_MARGIN),
            bottom=self.above_tiles,
        )

        if self.enemy_model.is_dead:
            self.on_enemy_died()

    def on_enemy_died(self) -> None:
        self.window.player_model.on_enemy_died(self.enemy_model)
        self.window.on_enemy_died(self.enemy_model)
        self.window.show_view(WorldView())

    def on_resize(self, width: float, height: float) -> None:
        # There is no superclass method, but this method definitely gets called.
        self.update_background()


def main() -> None:
    try:
        GameWindow()
        arcade.run()  # type: ignore
    except KeyboardInterrupt:
        pass
