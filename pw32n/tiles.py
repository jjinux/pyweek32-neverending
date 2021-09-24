from typing import NamedTuple

from pw32n import sprite_images


class Tile(NamedTuple):
    sprite_image: sprite_images.SpriteImage
    is_walkable: bool


GRASS_TILE = Tile(sprite_images.GRASS_TILE_IMAGE, is_walkable=True)
BOX_CRATE_TILE = Tile(sprite_images.BOX_CRATE_TILE_IMAGE, is_walkable=False)
GRASS_SIDE_VIEW_TILE = Tile(sprite_images.GRASS_SIDE_VIEW_TILE_IMAGE, is_walkable=True)
