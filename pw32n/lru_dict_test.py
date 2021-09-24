import unittest

from pw32n.lru_dict import LRUDict


class LRUDictTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.capacity = 3
        self.lru_dict: LRUDict[str, str] = LRUDict(self.capacity)

    def test_returns_default_for_missing_key(self) -> None:
        self.assertEqual(self.lru_dict.get("missing", "default"), "default")
        self.assertEqual(self.lru_dict.get("missing"), None)

    def test_stores_a_limited_number_of_things(self) -> None:
        for letter in "abcd":
            self.lru_dict.put(letter, letter)
        self.assertEqual(self.lru_dict.get("b"), "b")
        self.assertEqual(self.lru_dict.get("d"), "d")
        self.assertEqual(self.lru_dict.get("a"), None)
