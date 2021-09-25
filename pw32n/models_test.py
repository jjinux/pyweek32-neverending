import random
import unittest
from unittest.mock import patch, Mock

from pw32n.geography import OriginPoint
from pw32n import sprite_images, battle_moves
from pw32n.models import (
    CombatantModel,
    PlayerModel,
    EnemyModel,
    pick_enemy_strength,
    _pick_enemy_strength_non_random,
    MIN_INITIAL_ENEMY_STRENGTH_TO_PICK,
    RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH,
    IdleState,
    WarmingUpState,
    ExecutingMoveState,
    CoolingDownState,
    StunnedState,
    BATTLE_MOVE_WORKFLOW,
)
from pw32n.units import Secs


class CombatantModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.model = CombatantModel()

    def test_is_min_strength_by_default(self) -> None:
        self.assertEqual(self.model.strength, self.model.MIN_STRENGTH)

    def test_can_go_above_min_strength(self) -> None:
        self.model.strength = 2.0
        self.assertEqual(self.model.strength, 2.0)

    def test_cannot_go_below_min_strength(self) -> None:
        self.model.strength = -1.0
        self.assertEqual(self.model.strength, self.model.MIN_STRENGTH)

    def test_on_battle_view_begin_keeps_track_of_strength_at_the_beginning_of_battle(
        self,
    ) -> None:
        initial = 10.0
        self.model.strength = initial
        self.model.on_battle_view_begin()
        self.strength = 0.0
        self.assertEqual(self.model.strength_at_the_beginning_of_battle, initial)

    def test_on_attacked(self) -> None:
        self.model.strength = 1.0
        self.model.on_attacked(100.0)
        self.assertEqual(self.model.strength, self.model.MIN_STRENGTH)

    def test_on_attacked_when_dodging(self) -> None:
        self.model.strength = 5.0
        self.model.dodging = True
        self.model.on_attacked(5.0)
        self.assertEqual(self.model.strength, 5.0)

    def test_on_attacked_when_stunned(self) -> None:
        self.model.strength = 5.0
        self.model.state = StunnedState()
        self.model.on_attacked(5.0)
        self.assertEqual(self.model.strength, 5.0)

    def test_battle_move_workflow(self) -> None:
        self.assertIsInstance(self.model.state, IdleState)
        self.assertIsNone(self.model.current_workflow)
        self.assertIsNone(self.model.current_battle_move)
        self.assertIsNone(self.model.other)

        other = CombatantModel()
        other.strength = battle_moves.JAB.base_strength
        self.model.attempt_battle_move(battle_moves.JAB, other)
        self.assertEqual(self.model.current_battle_move, battle_moves.JAB)
        self.assertEqual(self.model.other, other)
        self.assertIsNotNone(self.model.current_workflow)
        self.assertEqual(self.model.current_workflow.name, BATTLE_MOVE_WORKFLOW)

        num_steps = len(self.model.current_workflow.steps)
        saw_warming_up_state = False
        saw_executing_move_state = False
        saw_cooling_down_state = False
        saw_idle_state_again = False

        for i in range(num_steps):
            self.model.on_battle_view_update(Secs(1.0))
            if isinstance(self.model.state, WarmingUpState):
                saw_warming_up_state = True
            elif isinstance(self.model.state, ExecutingMoveState):
                saw_executing_move_state = True
            elif isinstance(self.model.state, CoolingDownState):
                saw_cooling_down_state = True
            elif isinstance(self.model.state, IdleState):
                saw_idle_state_again = True

        self.assertTrue(saw_warming_up_state)
        self.assertTrue(saw_executing_move_state)
        self.assertTrue(saw_cooling_down_state)
        self.assertTrue(saw_idle_state_again)
        self.assertEqual(other.strength, 0.0)

        self.assertIsNone(self.model.current_workflow)
        self.assertIsNone(self.model.current_battle_move)
        self.assertIsNone(self.model.other)

    def test_battle_move_workflow_for_dodging(self) -> None:
        self.assertFalse(self.model.dodging)
        other = CombatantModel()
        self.model.attempt_battle_move(battle_moves.DODGE, other)
        num_steps = len(self.model.current_workflow.steps)
        for i in range(num_steps):
            self.model.on_battle_view_update(Secs(1.0))
            if isinstance(self.model.state, ExecutingMoveState):
                self.assertTrue(self.model.dodging)
            elif isinstance(self.model.state, CoolingDownState):
                self.assertFalse(self.model.dodging)
        self.assertFalse(self.model.dodging)

    def test_attempt_battle_move_exits_early_when_not_idle(self) -> None:
        self.model.state = WarmingUpState()
        other = CombatantModel()
        self.model.attempt_battle_move(battle_moves.JAB, other)
        self.assertIsNone(self.model.current_workflow)


class PlayerModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.player_model = PlayerModel()

    def test_min_strength(self) -> None:
        self.assertEqual(self.player_model.strength, self.player_model.MIN_STRENGTH)

    def test_on_world_view_update_makes_you_lose_strength_while_walking(self) -> None:
        initial_strength = Secs(2.0)
        self.player_model.strength = initial_strength
        self.player_model.on_world_view_update(0.0)
        self.assertEqual(self.player_model.strength, initial_strength)

        self.player_model.on_world_view_update(
            PlayerModel.TIME_BEFORE_LOSING_STRENGTH_WHILE_WALKING
        )
        self.assertEqual(
            self.player_model.strength,
            initial_strength - PlayerModel.AMOUNT_OF_STRENGTH_LOST_WHILE_WALKING,
        )

    def test_on_enemy_died_gives_strength_to_the_player(self) -> None:
        strength_at_the_beginning_of_battle = 10.0
        self.enemy_model = EnemyModel(
            sprite_image=sprite_images.ZOMBIE_IMAGE,
            position=OriginPoint(0, 0),
            strength=strength_at_the_beginning_of_battle,
            player_model=self.player_model,
        )
        self.enemy_model.strength_at_the_beginning_of_battle = (
            strength_at_the_beginning_of_battle
        )
        self.player_model.on_enemy_died(self.enemy_model)
        self.assertEqual(
            self.player_model.strength,
            PlayerModel.MIN_STRENGTH + strength_at_the_beginning_of_battle,
        )


class EnemyModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.player_model = PlayerModel()
        self.enemy_model = EnemyModel(
            sprite_image=sprite_images.ZOMBIE_IMAGE,
            position=OriginPoint(0, 0),
            strength=10.0,
            player_model=self.player_model,
        )

    def test_dying(self) -> None:
        self.assertFalse(self.enemy_model.is_dead)
        self.enemy_model.strength -= 100.0
        self.assertEqual(self.enemy_model.strength, 0.0)
        self.assertTrue(self.enemy_model.is_dead)

    @patch.object(CombatantModel, "attempt_battle_move")
    @patch.object(random, "choice", return_value=battle_moves.DODGE)
    @patch.object(random, "randrange", return_value=0)
    def test_on_battle_view_update(
        self, m_randrange: Mock, m_choice: Mock, m_attempt_battle_move: Mock
    ) -> None:
        self.enemy_model.on_battle_view_update(Secs(0.0))
        m_attempt_battle_move.assert_called_once_with(
            battle_moves.DODGE, self.enemy_model.player_model
        )

    @patch.object(CombatantModel, "attempt_battle_move")
    def test_on_battle_view_update_exits_early_when_not_idle(
        self, m_attempt_battle_move: Mock
    ) -> None:
        self.enemy_model.state = ExecutingMoveState()
        self.enemy_model.on_battle_view_update(Secs(0.0))
        m_attempt_battle_move.assert_not_called()


class PickEnemyStrengthTestCase(unittest.TestCase):
    def test__pick_enemy_strength_non_random_short_distance(self) -> None:
        op = OriginPoint(1, 1)
        self.assertEqual(
            _pick_enemy_strength_non_random(op), MIN_INITIAL_ENEMY_STRENGTH_TO_PICK
        )

    def test__pick_enemy_strength_non_random_medium_distance(self) -> None:
        distance = 10_000
        op = OriginPoint(0, 10_000)
        self.assertEqual(
            _pick_enemy_strength_non_random(op),
            distance * RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH,
        )

    def test_pick_enemy_strength_short_distance(self) -> None:
        op = OriginPoint(0, 10)
        self.assertEqual(pick_enemy_strength(op), MIN_INITIAL_ENEMY_STRENGTH_TO_PICK)

    def test_pick_enemy_strength_medium_distance(self) -> None:
        for i in range(10):
            op = OriginPoint(0, 1000)
            if pick_enemy_strength(op) > MIN_INITIAL_ENEMY_STRENGTH_TO_PICK:
                break
        else:
            raise AssertionError(
                f"pick_enemy_strength always returns {MIN_INITIAL_ENEMY_STRENGTH_TO_PICK}"
            )
