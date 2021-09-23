from typing import NamedTuple


class TileDetails(NamedTuple):
    filename: str
    scaling: float


PLAYER_TILE = TileDetails(
    ":resources:images/animated_characters/female_person/femalePerson_idle.png",
    scaling=0.4,
)

# It's 64x64, and that's what I want.
GRASS_TILE = TileDetails(":resources:images/topdown_tanks/tileGrass2.png", scaling=1.0)

# It's 128x128, and I want 64x64.
BOX_CRATE_TILE = TileDetails(":resources:images/tiles/boxCrate_double.png", scaling=0.5)
