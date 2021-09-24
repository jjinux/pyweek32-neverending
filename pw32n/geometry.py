"""This module contains all sorts of things related to distances, positions, etc.

There are basically two types of distances. An AdventureDistance measures a distance based on how adventure and
piglet think of things (although I'm using ints to make my life easier). An OriginDistance measures a distance from
where the character first started. It's an int (so that it can be arbitrarily large and accurate). I'm using type
annotations to avoid mixing up the two of them.

"""

from typing import Iterator, NamedTuple

AdventureDistance = int
OriginDistance = int


class AdventurePoint(NamedTuple):
    x: AdventureDistance
    y: AdventureDistance


class OriginPoint(NamedTuple):
    x: OriginDistance
    y: OriginDistance


class TilePointDiff(NamedTuple):
    added: set[OriginPoint]
    removed: set[OriginPoint]


class Geometry:

    """This class wraps up a bunch of "context" about the game's geometry."""

    def __init__(self) -> None:
        self.tile_width: AdventureDistance = 64
        self.tile_height: AdventureDistance = 64
        self.screen_width: AdventureDistance = 800
        self.screen_height: AdventureDistance = 600
        self.min_screen_width: AdventureDistance = 800
        self.min_screen_height: AdventureDistance = 600
        self.initial_position = OriginPoint(0, 0)
        self.position = self.initial_position

    def align_x(self, x: OriginDistance) -> OriginDistance:
        """See align_point."""
        if x % self.tile_width == 0:
            return x
        return x - x % self.tile_width

    def align_y(self, y: OriginDistance) -> OriginDistance:
        """See align_point."""
        if y % self.tile_height == 0:
            return y
        return y + (self.tile_height - y % self.tile_height)

    def align_point(self, p: OriginPoint) -> OriginPoint:
        """When laying down tiles, we need to make sure we "align" them.

        If you're in the middle of a tile, we push you to the top, left of the tile.

        """
        return OriginPoint(self.align_x(p.x), self.align_y(p.y))

    def is_aligned(self, p: OriginPoint) -> bool:
        return p == self.align_point(p)

    def left_tile_boundary(self) -> OriginDistance:
        """We want to lay down tiles so that they go between 1-2 tiles past each side of the screen."""
        # align_x may pull it further left so that it's it's more than a tile_width from the left
        # of the screen.
        return self.align_x(self.position.x - self.screen_width // 2 - self.tile_width)

    def right_tile_boundary(self) -> OriginDistance:
        """See left_tile_boundary."""
        # align_x may pull it further left so that it's less than 3 tile_widths from the right
        # of the screen. The 3 is helpful because the tile begins *to the left of* the player
        # sprite.
        return self.align_x(
            self.position.x + self.screen_width // 2 + 3 * self.tile_width
        )

    def top_tile_boundary(self) -> OriginDistance:
        """See left_tile_boundary."""
        # align_y may pull it further up so that it's more than a tile_height from the top of the
        # screen.
        return self.align_y(
            self.position.y + self.screen_height // 2 + self.tile_height
        )

    def bottom_tile_boundary(self) -> OriginDistance:
        """See left_tile_boundary."""
        # align_y may pull it further up so that it's less than 3 tile_heights from the bottom
        # of the screen. The 3 is helpful because the tile begins *above* the player sprite.
        return self.align_y(
            self.position.y - self.screen_height // 2 - 3 * self.tile_height
        )

    def generate_tile_points(self) -> Iterator[OriginPoint]:
        for x in range(
            self.left_tile_boundary(), self.right_tile_boundary(), self.tile_width
        ):
            for y in range(
                self.top_tile_boundary(), self.bottom_tile_boundary(), -self.tile_height
            ):
                yield OriginPoint(x, y)

    def diff_tile_points(
        self, prev_tile_points: set[OriginPoint], new_tile_points: set[OriginPoint]
    ) -> TilePointDiff:
        return TilePointDiff(
            added=(new_tile_points - prev_tile_points),
            removed=(prev_tile_points - new_tile_points),
        )

    def center_of_screen_x(self) -> AdventureDistance:
        return self.screen_width // 2

    def center_of_screen_y(self) -> AdventureDistance:
        return self.screen_height // 2

    def center_of_screen(self) -> AdventurePoint:
        return AdventurePoint(self.center_of_screen_x(), self.center_of_screen_y())

    def origin_point_to_adventure_point(self, op: OriginPoint) -> AdventurePoint:
        return AdventurePoint(
            op.x - self.position.x,
            op.y - self.position.y,
        )
