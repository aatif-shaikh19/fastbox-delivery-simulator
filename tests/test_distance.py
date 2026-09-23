import math
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.distance import euclidean_distance


class TestEuclideanDistance(unittest.TestCase):
    def test_identical_points(self):
        self.assertAlmostEqual(euclidean_distance((0, 0), (0, 0)), 0.0)
        self.assertAlmostEqual(euclidean_distance((42.5, -17.2), (42.5, -17.2)), 0.0)

    def test_known_distances(self):
        # 3-4-5 right triangle
        self.assertAlmostEqual(euclidean_distance((0, 0), (3, 4)), 5.0)
        self.assertAlmostEqual(euclidean_distance((1, 1), (4, 5)), 5.0)

        # Diagonal
        self.assertAlmostEqual(euclidean_distance((0, 0), (5, 5)), math.sqrt(50))

        # Assignment coordinates (e.g. W1 at [0,0] to P1 destination [30, 40])
        self.assertAlmostEqual(euclidean_distance((0, 0), (30, 40)), 50.0)

    def test_negative_coordinates(self):
        self.assertAlmostEqual(euclidean_distance((-10, -20), (10, 20)), math.sqrt(2000))

    def test_symmetry(self):
        p1 = (12.3, 45.6)
        p2 = (78.9, 3.2)
        self.assertAlmostEqual(euclidean_distance(p1, p2), euclidean_distance(p2, p1))

    def test_accepts_lists_and_tuples(self):
        self.assertAlmostEqual(euclidean_distance([0, 0], [3, 4]), 5.0)
        self.assertAlmostEqual(euclidean_distance((0, 0), [3, 4]), 5.0)


if __name__ == "__main__":
    unittest.main()
