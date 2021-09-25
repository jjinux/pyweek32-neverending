import unittest

from pw32n.geography import OriginPoint
from pw32n.models import (
    CombatantModel,
    PlayerModel,
    EnemyModel,
    pick_enemy_strength,
    _pick_enemy_strength_non_random,
    MIN_INITIAL_ENEMY_STRENGTH_TO_PICK,
    RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH,
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

    def test_on_attacked(self) -> None:
        self.model.strength = 1.0
        self.model.on_attacked(100.0)
        self.assertEqual(self.model.strength, self.model.MIN_STRENGTH)


class PlayerModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.model = PlayerModel()

    def test_min_strength(self) -> None:
        self.assertEqual(self.model.strength, self.model.MIN_STRENGTH)

    def test_on_world_view_update_makes_you_lose_strength_while_walking(self) -> None:
        initial_strength = Secs(2.0)
        self.model.strength = initial_strength
        self.model.on_world_view_update(0.0)
        self.assertEqual(self.model.strength, initial_strength)

        self.model.on_world_view_update(
            PlayerModel.TIME_BEFORE_LOSING_STRENGTH_WHILE_WALKING
        )
        self.assertEqual(
            self.model.strength,
            initial_strength - PlayerModel.AMOUNT_OF_STRENGTH_LOST_WHILE_WALKING,
        )


class EnemyModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.player_model = PlayerModel()
        self.enemy_model = EnemyModel(
            position=OriginPoint(0, 0), strength=10.0, player_model=self.player_model
        )

    def test_dying(self) -> None:
        self.assertFalse(self.enemy_model.is_dead)
        self.enemy_model.strength -= 100.0
        self.assertEqual(self.enemy_model.strength, 0.0)
        self.assertTrue(self.enemy_model.is_dead)


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
