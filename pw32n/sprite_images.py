from typing import NamedTuple


class SpriteImage(NamedTuple):
    filename: str
    scaling: float


# These are really just image filenames, etc. Hence, they end in IMAGE. The ones that are meant
# to serve as background tiles end in TILE_IMAGE.

PLAYER_IMAGE = SpriteImage(
    ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
    scaling=0.4,
)

# It's 64x64, and that's what I want.
GRASS_TILE_IMAGE = SpriteImage(
    ":resources:images/topdown_tanks/tileGrass2.png", scaling=1.0
)

# It's 128x128, and I want 64x64.
BOX_CRATE_TILE_IMAGE = SpriteImage(
    ":resources:images/tiles/boxCrate_double.png", scaling=0.5
)

# It's 128x128, and I want 64x64.
GRASS_SIDE_VIEW_TILE_IMAGE = SpriteImage(
    ":resources:images/tiles/grassMid.png", scaling=0.5
)

# It's 128x128, and I want 128x128.
PLAYER_SIDE_VIEW_IMAGE = SpriteImage(
    ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
    scaling=1.0,
)

# It's 128x128, and I want 128x128.
SLIME_SIDE_VIEW_IMAGE = SpriteImage(
    ":resources:images/enemies/slimeGreen.png", scaling=1.0
)
