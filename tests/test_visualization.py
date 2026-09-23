import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.visualization import render_ascii_map


class TestVisualization(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            "warehouses": {"W1": (0.0, 0.0), "W2": (50.0, 50.0)},
            "agents": {"A1": (10.0, 10.0)},
            "packages": [
                {"id": "P1", "warehouse": "W1", "destination": (25.0, 25.0)},
                {"id": "P2", "warehouse": "W2", "destination": (45.0, 45.0)},
            ],
        }

    def test_render_contains_markers_and_legend(self):
        output = render_ascii_map(self.sample_data, grid_width=30, grid_height=10)

        # Check title and legend
        self.assertIn("FastBox Simulation Map", output)
        self.assertIn("Legend:", output)
        self.assertIn("W : Warehouse", output)
        self.assertIn("A : Agent Start Position", output)
        self.assertIn("P : Package Destination", output)

        # Check markers on map
        self.assertIn("W", output)
        self.assertIn("A", output)
        self.assertIn("P", output)

    def test_empty_data(self):
        output = render_ascii_map({})
        self.assertIn("No coordinate data available", output)

    def test_overlap_marker(self):
        # Warehouse and Agent at exact same coordinates
        data = {
            "warehouses": {"W1": (10.0, 10.0)},
            "agents": {"A1": (10.0, 10.0)},
            "packages": [],
        }
        output = render_ascii_map(data, grid_width=20, grid_height=10)
        self.assertIn("*", output)

    def test_custom_dimensions(self):
        w, h = 25, 8
        output = render_ascii_map(self.sample_data, grid_width=w, grid_height=h)
        lines = output.splitlines()
        # Find lines with borders '|'
        grid_rows = [line for line in lines if line.startswith("|") and line.endswith("|")]
        self.assertEqual(len(grid_rows), h)
        for row in grid_rows:
            self.assertEqual(len(row), w + 2)  # +2 for enclosing '|'


if __name__ == "__main__":
    unittest.main()
