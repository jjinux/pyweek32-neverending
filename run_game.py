#!/usr/bin/env python3.9

import sys

import arcade

MIN_PYTHON_VERSION = (3, 9)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "pyweek32-neverending"
CHARACTER_SCALING = 1
TILE_SCALING = 0.5


class MainView(arcade.View):
    def __init__(self):
        super().__init__()
        self.wall_list = None
        self.player_list = None
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        coordinate_list = [[512, 96], [256, 96], [768, 96]]

        for coordinate in coordinate_list:
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
            )
            wall.position = coordinate
            self.wall_list.append(wall)

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.player_list.draw()

    def on_key_press(self, key, _modifiers):
        """If user hits escape, go back to the main menu view"""
        if key == arcade.key.ESCAPE:
            game_over_view = GameOverView()
            self.window.show_view(game_over_view)


class GameOverView(arcade.View):
    """Class to manage the game over view"""

    def on_show(self):
        """Called when switching to this view"""
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Draw the game over view"""
        arcade.start_render()
        arcade.draw_text(
            "Game Over - press ESCAPE to advance",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            30,
            anchor_x="center",
        )

    def on_key_press(self, key, _modifiers):
        """If user hits escape, go back to the main menu view"""
        if key == arcade.key.ESCAPE:
            main_view = MainView()
            main_view.setup()
            self.window.show_view(main_view)


def main():
    if sys.version_info[:2] < MIN_PYTHON_VERSION:
        sys.exit(f"This game requires Python {'.'.join(map(str, MIN_PYTHON_VERSION))}")

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    main_view = MainView()
    main_view.setup()
    window.show_view(main_view)
    arcade.run()


if __name__ == "__main__":
    main()
