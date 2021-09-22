import unittest

from pw32n import geometry


class TestGeometry(unittest.TestCase):

    def test_add(self):
        self.assertEqual(geometry.add(1, 2), 3)
