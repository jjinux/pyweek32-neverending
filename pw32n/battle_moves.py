from typing import NamedTuple

from pw32n.units import Secs


class BattleMove(NamedTuple):
    warmup_period: Secs
    execution_period: Secs
    cooldown_period: Secs


DODGE = BattleMove(
    warmup_period=Secs(0.09), execution_period=Secs(1.0), cooldown_period=Secs(0.3)
)
JAB = BattleMove(
    warmup_period=Secs(0.2), execution_period=Secs(0.3), cooldown_period=Secs(0.2)
)
UPPERCUT = BattleMove(
    warmup_period=Secs(0.8), execution_period=Secs(0.8), cooldown_period=Secs(0.3)
)
