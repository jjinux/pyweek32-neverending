# See: https://mypy.readthedocs.io/en/latest/runtime_troubles.html?highlight=forward#class-name-forward-references
from __future__ import annotations

import math
import random

from pw32n import geography
from pw32n import sprite_images
from pw32n.units import Secs

MIN_INITIAL_ENEMY_STRENGTH_TO_PICK = 0.1
RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH = 0.001
JAB_STRENGTH = 0.1
UPPERCUT_STRENGTH = 0.2


class CombatantModel:
    # Subclasses may want to override this.
    MIN_STRENGTH = 0.0

    def __init__(self) -> None:
        self.__strength = self.MIN_STRENGTH
        self.strength_at_the_beginning_of_battle = 0.0

    @property
    def strength(self) -> float:
        return self.__strength

    @strength.setter
    def strength(self, strength: float) -> None:
        self.__strength = max(strength, self.MIN_STRENGTH)

    def on_battle_view_begin(self) -> None:
        self.strength_at_the_beginning_of_battle = self.strength

    def on_attacked(self, power: float) -> None:
        self.strength -= power


class PlayerModel(CombatantModel):
    # Players can't die.
    MIN_STRENGTH = 1.0

    TIME_BEFORE_LOSING_STRENGTH_WHILE_WALKING = Secs(2.0)
    AMOUNT_OF_STRENGTH_LOST_WHILE_WALKING = 0.1

    def __init__(self) -> None:
        super().__init__()
        self.time_since_losing_strength_while_walking = Secs(0.0)

    def on_world_view_update(self, delta_time: float) -> None:
        self.time_since_losing_strength_while_walking += delta_time
        if (
            self.time_since_losing_strength_while_walking
            >= self.TIME_BEFORE_LOSING_STRENGTH_WHILE_WALKING
        ):
            self.strength -= self.AMOUNT_OF_STRENGTH_LOST_WHILE_WALKING
            self.time_since_losing_strength_while_walking = Secs(0.0)

    def on_enemy_died(self, enemy: EnemyModel) -> None:
        self.strength += enemy.strength_at_the_beginning_of_battle


class EnemyModel(CombatantModel):
    AVERAGE_NUMBER_OF_TICKS_BEFORE_ATTACKING = 45

    def __init__(
        self,
        sprite_image: sprite_images.SpriteImage,
        position: geography.OriginPoint,
        strength: float,
        player_model: PlayerModel,
    ) -> None:
        super().__init__()
        self.sprite_image = sprite_image
        self.position = position
        self.strength = strength
        self.player_model = player_model

    @property
    def is_dead(self) -> bool:
        """Only enemies can die. The player is immortal."""
        return self.strength == 0.0

    def on_battle_view_update(self, delta_time: float) -> None:
        if random.randrange(self.AVERAGE_NUMBER_OF_TICKS_BEFORE_ATTACKING) == 0:
            attack = random.choice([JAB_STRENGTH, UPPERCUT_STRENGTH])
            self.player_model.on_attacked(attack)


def pick_enemy_strength(op: geography.OriginPoint) -> float:
    return random.uniform(
        MIN_INITIAL_ENEMY_STRENGTH_TO_PICK, _pick_enemy_strength_non_random(op)
    )


def _pick_enemy_strength_non_random(op: geography.OriginPoint) -> float:
    """As you get further away from the origin, the enemies get stronger."""
    distance = math.sqrt(op.x ** 2 + op.y ** 2)
    strength_based_on_distance = distance * RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH
    return max(MIN_INITIAL_ENEMY_STRENGTH_TO_PICK, strength_based_on_distance)
