import math
import random

from pw32n import geography

MIN_INITIAL_ENEMY_STRENGTH_TO_PICK = 0.1
RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH = 0.001
JAB_STRENGTH = 0.05
UPPERCUT_STRENGTH = 0.1


class CombatantModel:
    # Subclasses may want to override this.
    MIN_STRENGTH = 0.0

    def __init__(self) -> None:
        self.__strength = self.MIN_STRENGTH

    @property
    def strength(self) -> float:
        return self.__strength

    @strength.setter
    def strength(self, strength: float) -> None:
        self.__strength = max(strength, self.MIN_STRENGTH)

    def on_attacked(self, power: float) -> None:
        self.strength -= power


class PlayerModel(CombatantModel):
    # Players can't die.
    MIN_STRENGTH = 1.0


class EnemyModel(CombatantModel):
    def __init__(self, position: geography.OriginPoint, strength: float) -> None:
        super().__init__()
        self.position = position
        self.strength = strength

    @property
    def is_dead(self) -> bool:
        """Only enemies can die. The player is immortal."""
        return self.strength == 0.0


def pick_enemy_strength(op: geography.OriginPoint) -> float:
    return random.uniform(
        MIN_INITIAL_ENEMY_STRENGTH_TO_PICK, _pick_enemy_strength_non_random(op)
    )


def _pick_enemy_strength_non_random(op: geography.OriginPoint) -> float:
    """As you get further away from the origin, the enemies get stronger."""
    distance = math.sqrt(op.x ** 2 + op.y ** 2)
    strength_based_on_distance = distance * RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH
    return max(MIN_INITIAL_ENEMY_STRENGTH_TO_PICK, strength_based_on_distance)
