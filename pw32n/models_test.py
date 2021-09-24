import unittest

from pw32n.geography import OriginPoint
from pw32n.models import PlayerModel, EnemyModel, pick_enemy_strength


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
    def test_small_distances(self) -> None:
        for i in range(3):
            op = OriginPoint(0, 10)
            self.assertEqual(pick_enemy_strength(op), 0.1)

    def test_medium_distances(self) -> None:
        saw_small = False
        saw_big = False
        for i in range(100):
            op = OriginPoint(0, 10_000)
            strength = pick_enemy_strength(op)
            if strength < 5.0:
                saw_small = True
            if strength >= 5.0:
                saw_big = True
            if strength > 10.0:
                raise AssertionError(f"Unexpectedly large: {strength}")
            if saw_small and saw_big:
                break
