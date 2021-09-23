import unittest

from pw32n import geometry


class SmallGeometry(geometry.Geometry):

    """It's easier to understand things if you use smaller numbers."""

    def __init__(self) -> None:
        super().__init__()
        self.tile_width: geometry.AdventureDistance = 5
        self.tile_height: geometry.AdventureDistance = 5
        self.screen_width: geometry.AdventureDistance = 100
        self.screen_height: geometry.AdventureDistance = 80
        self.min_screen_width: geometry.AdventureDistance = 100
        self.min_screen_height: geometry.AdventureDistance = 80
        self.position = geometry.OriginPoint(20, 20)


class GeometryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.geo = SmallGeometry()

    def test_adventure_point(self) -> None:
        self.assertTrue(geometry.AdventurePoint(1, 2))

    def test_origin_point(self) -> None:
        self.assertTrue(geometry.OriginPoint(1, 2))

    def test_align_x(self) -> None:
        for (input, expected) in (
            (0, 0),
            (-5, -5),
            (5, 5),
            (10, 10),
            (1, 0),
            (-1, -5),
            (-4, -5),
            (-6, -10),
            (6, 5),
        ):
            self.assertEqual(self.geo.align_x(input), expected, (input, expected))

    def test_align_y(self) -> None:
        for (input, expected) in (
            (0, 0),
            (-5, -5),
            (5, 5),
            (10, 10),
            (1, 5),
            (-1, 0),
            (-4, 0),
            (-6, -5),
            (6, 10),
        ):
            self.assertEqual(self.geo.align_y(input), expected, (input, expected))

    def test_align_point(self) -> None:
        self.assertEqual(
            self.geo.align_point(geometry.OriginPoint(0, 0)), geometry.OriginPoint(0, 0)
        )

    def test_is_aligned(self) -> None:
        self.assertTrue(self.geo.is_aligned(geometry.OriginPoint(0, 0)))
        self.assertFalse(self.geo.is_aligned(geometry.OriginPoint(1, 1)))

    # Ugh, these next 4 tests are terrible. I walked through the logic by hand once.
    # Consider this snapshot testing.

    def test_left_tile_boundary(self) -> None:
        self.assertEqual(self.geo.left_tile_boundary(), geometry.OriginDistance(-35))

    def test_right_tile_boundary(self) -> None:
        self.assertEqual(self.geo.right_tile_boundary(), geometry.OriginDistance(85))

    def test_top_tile_boundary(self) -> None:
        self.assertEqual(self.geo.top_tile_boundary(), geometry.OriginDistance(65))

    def test_bottom_tile_boundary(self) -> None:
        self.assertEqual(self.geo.bottom_tile_boundary(), geometry.OriginDistance(-35))

    def test_generate_tile_points(self) -> None:
        tile_points = list(self.geo.generate_tile_points())
        self.assertGreater(len(tile_points), 0)
        for p in tile_points:
            self.assertTrue(self.geo.is_aligned(p))
            self.assertLessEqual(self.geo.left_tile_boundary(), p.x)
            self.assertLess(p.x, self.geo.right_tile_boundary())
            self.assertGreaterEqual(self.geo.top_tile_boundary(), p.y)
            self.assertGreater(p.y, self.geo.bottom_tile_boundary())

    def test_diff_tile_points(self) -> None:
        p0 = geometry.OriginPoint(0, 0)
        p1 = geometry.OriginPoint(1, 1)
        p2 = geometry.OriginPoint(1, 2)
        prev_tile_points = {p0, p1}
        new_tile_points = {p1, p2}
        diff = self.geo.diff_tile_points(prev_tile_points, new_tile_points)
        self.assertSetEqual(diff.removed, {p0})
        self.assertEqual(diff.added, {p2})

    def test_center_of_screen_x(self) -> None:
        self.assertEqual(self.geo.center_of_screen_x(), 50)

    def test_center_of_screen_y(self) -> None:
        self.assertEqual(self.geo.center_of_screen_y(), 40)

    def test_center_of_screen(self) -> None:
        self.assertEqual(self.geo.center_of_screen(), geometry.AdventurePoint(50, 40))

    def test_origin_point_to_adventure_point(self) -> None:
        center = self.geo.center_of_screen()
        op = geometry.OriginPoint(
            self.geo.position.x + 1,
            self.geo.position.y + 1,
        )
        expected_ap = geometry.AdventurePoint(1, 1)
        self.assertEqual(self.geo.origin_point_to_adventure_point(op), expected_ap)
