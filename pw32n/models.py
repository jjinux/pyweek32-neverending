# See: https://mypy.readthedocs.io/en/latest/runtime_troubles.html?highlight=forward#class-name-forward-references
from __future__ import annotations

import math
import random
from typing import NamedTuple, Union

from pw32n import geography, sprite_images, battle_moves
from pw32n.timed_workflow import TimedWorkflow, TimedStep
from pw32n.units import Secs

MIN_INITIAL_ENEMY_STRENGTH_TO_PICK = 0.1
RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH = 0.001


class IdleState(NamedTuple):
    pass


class WarmingUpState(NamedTuple):
    pass


class ExecutingMoveState(NamedTuple):
    pass


class CoolingDownState(NamedTuple):
    pass


class StunnedState(NamedTuple):
    pass


CombatantState = Union[
    IdleState, WarmingUpState, ExecutingMoveState, CoolingDownState, StunnedState
]

BATTLE_MOVE_WORKFLOW = "BATTLE_MOVE_WORKFLOW"
STUNNED_WORKFLOW = "STUNNED_WORKFLOW"


class CombatantModel:
    # Subclasses may want to override this.
    MIN_STRENGTH = 0.0

    def __init__(self) -> None:
        self.__strength = self.MIN_STRENGTH
        self.strength_at_the_beginning_of_battle = 0.0
        self.state: CombatantState = IdleState()
        self.current_workflow: TimedWorkflow = None
        self.current_battle_move: battle_moves.BattleMove = None
        self.other: CombatantModel = None
        self.dodging = False
        self.flip_sprite_upside_down = False

    @property
    def strength(self) -> float:
        return self.__strength

    @strength.setter
    def strength(self, strength: float) -> None:
        self.__strength = max(strength, self.MIN_STRENGTH)

    def on_battle_view_begin(self) -> None:
        self.strength_at_the_beginning_of_battle = self.strength

    def on_attacked(self, power: float) -> None:
        if self.dodging or isinstance(self.state, StunnedState):
            return

        self.strength -= power
        self.current_workflow = TimedWorkflow(
            name=STUNNED_WORKFLOW,
            steps=[
                TimedStep(Secs(0.0), self.enter_stunned_period),
                TimedStep(battle_moves.STUNNED.execution_period, self.return_to_idle),
            ],
        )

    def attempt_battle_move(
        self, move: battle_moves.BattleMove, other: CombatantModel
    ) -> None:
        if not isinstance(self.state, IdleState):
            return
        self.current_battle_move = move
        self.other = other
        self.current_workflow = TimedWorkflow(
            name=BATTLE_MOVE_WORKFLOW,
            steps=[
                TimedStep(Secs(0.0), self.enter_warmup_period),
                TimedStep(move.warmup_period, self.enter_execution_period),
                TimedStep(move.execution_period, self.enter_cooldown_period),
                TimedStep(move.cooldown_period, self.return_to_idle),
            ],
        )

    def on_battle_view_update(self, delta_time: float) -> None:
        if self.current_workflow:
            self.current_workflow.on_update(delta_time)

    def enter_warmup_period(self, late_by: Secs) -> None:
        self.state = WarmingUpState()

    def enter_execution_period(self, late_by: Secs) -> None:
        self.state = ExecutingMoveState()
        if self.current_battle_move == battle_moves.DODGE:
            self.dodging = True
        else:
            self.other.on_attacked(self.current_battle_move.base_strength)

    def enter_cooldown_period(self, late_by: Secs) -> None:
        self.state = CoolingDownState()
        if self.current_battle_move == battle_moves.DODGE:
            self.dodging = False

    def enter_stunned_period(self, late_by: Secs) -> None:
        self.state = StunnedState()
        self.flip_sprite_upside_down = True

    def return_to_idle(self, late_by: Secs) -> None:
        self.state = IdleState()
        self.flip_sprite_upside_down = False

        # Remember to clean up.
        self.current_battle_move = None
        self.other = None
        self.current_workflow = None


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
        super().on_battle_view_update(delta_time)
        if not isinstance(self.state, IdleState):
            return
        if random.randrange(self.AVERAGE_NUMBER_OF_TICKS_BEFORE_ATTACKING) == 0:
            move = random.choice(
                [battle_moves.DODGE, battle_moves.JAB, battle_moves.UPPERCUT]
            )
            self.attempt_battle_move(move, self.player_model)


def pick_enemy_strength(op: geography.OriginPoint) -> float:
    return random.uniform(
        MIN_INITIAL_ENEMY_STRENGTH_TO_PICK, _pick_enemy_strength_non_random(op)
    )


def _pick_enemy_strength_non_random(op: geography.OriginPoint) -> float:
    """As you get further away from the origin, the enemies get stronger."""
    distance = math.sqrt(op.x ** 2 + op.y ** 2)
    strength_based_on_distance = distance * RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH
    return max(MIN_INITIAL_ENEMY_STRENGTH_TO_PICK, strength_based_on_distance)
