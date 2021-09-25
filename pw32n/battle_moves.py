from typing import NamedTuple

from pw32n.units import Secs


class BattleMove(NamedTuple):
    base_strength: float
    warmup_period: Secs
    execution_period: Secs
    cooldown_period: Secs

    # Which direction should the sprite move in in order to animate this move
    # assuming it's the player (-1, 0, or 1)?
    delta_x: int
    delta_y: int


DODGE = BattleMove(
    base_strength=0.0,
    warmup_period=Secs(0.09),
    execution_period=Secs(1.0),
    cooldown_period=Secs(0.2),
    delta_x=-1,
    delta_y=0,
)
JAB = BattleMove(
    base_strength=1,
    warmup_period=Secs(0.15),
    execution_period=Secs(0.15),
    cooldown_period=Secs(0.15),
    delta_x=1,
    delta_y=0,
)
UPPERCUT = BattleMove(
    base_strength=3,
    warmup_period=Secs(0.5),
    execution_period=Secs(0.5),
    cooldown_period=Secs(0.2),
    delta_x=0,
    delta_y=1,
)
STUNNED = BattleMove(
    base_strength=0.0,
    warmup_period=Secs(0.0),
    execution_period=Secs(0.4),
    cooldown_period=Secs(0.0),
    delta_x=0,
    delta_y=0,
)
