import unittest

from pw32n.geography import OriginPoint
from pw32n.models import (
    PlayerModel,
    EnemyModel,
    pick_enemy_strength,
    _pick_enemy_strength_non_random,
    MIN_INITIAL_ENEMY_STRENGTH_TO_PICK,
    RATIO_OF_DISTANCE_TO_ENEMY_STRENGTH,
)


class PlayerModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.player_model = PlayerModel()

    def test_is_min_strength_by_default(self) -> None:
        self.assertEqual(self.player_model.strength, self.player_model.MIN_STRENGTH)

    def test_can_go_above_min_strength(self) -> None:
        self.player_model.strength = 2.0
        self.assertEqual(self.player_model.strength, 2.0)

    def test_cannot_go_below_min_strength(self) -> None:
        self.player_model.strength = -1.0
        self.assertEqual(self.player_model.strength, self.player_model.MIN_STRENGTH)
        self.assertFalse(self.player_model.is_dead)


class EnemyModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.enemy_model = EnemyModel(strength=10.0)

    def test_dying(self) -> None:
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
