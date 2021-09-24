from typing import NamedTuple

from pw32n import sprite_images


class Tile(NamedTuple):
    sprite_image: sprite_images.SpriteImage


GRASS_TILE = Tile(sprite_images.GRASS_TILE_IMAGE)
BOX_CRATE_TILE = Tile(sprite_images.BOX_CRATE_TILE_IMAGE)
GRASS_SIDE_VIEW_TILE = Tile(sprite_images.GRASS_SIDE_VIEW_TILE_IMAGE)
