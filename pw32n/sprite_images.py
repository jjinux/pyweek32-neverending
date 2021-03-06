from typing import NamedTuple


class SpriteImage(NamedTuple):
    filename: str
    width: float


# These are really just image filenames, etc. Hence, they end in IMAGE. The ones that are meant
# to serve as background tiles end in TILE_IMAGE.

PLAYER_IMAGE = SpriteImage(
    ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
    width=128,
)

GRASS_TILE_IMAGE = SpriteImage(
    ":resources:images/topdown_tanks/tileGrass2.png", width=64
)

BOX_CRATE_TILE_IMAGE = SpriteImage(
    ":resources:images/tiles/boxCrate_double.png", width=128
)

GRASS_SIDE_VIEW_TILE_IMAGE = SpriteImage(
    ":resources:images/tiles/grassMid.png", width=128
)

ZOMBIE_IMAGE = SpriteImage(
    ":resources:images/animated_characters/zombie/zombie_idle.png", width=128
)

MALE_PERSON_IMAGE = SpriteImage(
    ":resources:images/animated_characters/male_person/malePerson_idle.png", width=128
)

FEMALE_PERSON_IMAGE = SpriteImage(
    ":resources:images/animated_characters/female_person/femalePerson_idle.png",
    width=128,
)

MALE_ADVENTURER_IMAGE = SpriteImage(
    ":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png",
    width=128,
)

ROBOT_IMAGE = SpriteImage(
    ":resources:images/animated_characters/robot/robot_idle.png", width=128
)
