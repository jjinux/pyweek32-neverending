import unittest

from pw32n.models import PlayerModel


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
