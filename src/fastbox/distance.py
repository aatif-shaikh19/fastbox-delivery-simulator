import math
from typing import Sequence

Point = tuple[float, float] | list[float] | Sequence[float]


def euclidean_distance(p1: Point, p2: Point) -> float:
    """Calculate the 2D Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
