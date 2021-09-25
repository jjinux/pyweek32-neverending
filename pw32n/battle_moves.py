from typing import NamedTuple

from pw32n.units import Secs


class BattleMove(NamedTuple):
    base_strength: float
    warmup_period: Secs
    execution_period: Secs
    cooldown_period: Secs


DODGE = BattleMove(
    base_strength=0.0,
    warmup_period=Secs(0.09),
    execution_period=Secs(1.0),
    cooldown_period=Secs(0.3),
)
JAB = BattleMove(
    base_strength=0.1,
    warmup_period=Secs(0.2),
    execution_period=Secs(0.3),
    cooldown_period=Secs(0.2),
)
UPPERCUT = BattleMove(
    base_strength=0.3,
    warmup_period=Secs(0.8),
    execution_period=Secs(0.8),
    cooldown_period=Secs(0.3),
)
