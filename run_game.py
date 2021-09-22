#!/usr/bin/env python3.9

import sys

import arcade

MIN_PYTHON_VERSION = (3, 9)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "pyweek32-neverending"


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()


def main():
    if sys.version_info[:2] < MIN_PYTHON_VERSION:
        sys.exit(
            f"This game requires Python {'.'.join(map(str, MIN_PYTHON_VERSION))}"
        )

    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
