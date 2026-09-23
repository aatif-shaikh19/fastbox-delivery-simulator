import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.assignment import assign_packages, find_nearest_agent


class TestAssignment(unittest.TestCase):
    def test_nearest_agent(self):
        agents = {
            "A1": (0.0, 0.0),
            "A2": (100.0, 100.0),
        }
        # Warehouse at (1, 1) is closer to A1
        self.assertEqual(find_nearest_agent((1.0, 1.0), agents), "A1")
        # Warehouse at (90, 90) is closer to A2
        self.assertEqual(find_nearest_agent((90.0, 90.0), agents), "A2")

    def test_tie_case(self):
        # A1 and A2 are both distance 5.0 from warehouse (5, 0)
        # A1 is at (0, 0), A2 is at (10, 0)
        agents = {
            "A2": (10.0, 0.0),
            "A1": (0.0, 0.0),
        }
        warehouse_loc = (5.0, 0.0)
        # Deterministic lexicographical tie-break: 'A1' < 'A2'
        self.assertEqual(find_nearest_agent(warehouse_loc, agents), "A1")

        # Reverse names: 'B1' and 'B2'
        agents_b = {
            "B2": (0.0, 0.0),
            "B1": (10.0, 0.0),
        }
        self.assertEqual(find_nearest_agent(warehouse_loc, agents_b), "B1")

    def test_multiple_packages_same_warehouse(self):
        warehouses = {"W1": (0.0, 0.0), "W2": (100.0, 100.0)}
        agents = {"A1": (5.0, 5.0), "A2": (95.0, 95.0)}
        packages = [
            {"id": "P1", "warehouse": "W1", "destination": (10.0, 10.0)},
            {"id": "P2", "warehouse": "W1", "destination": (20.0, 20.0)},
            {"id": "P3", "warehouse": "W1", "destination": (30.0, 30.0)},
            {"id": "P4", "warehouse": "W2", "destination": (90.0, 90.0)},
        ]

        assignments = assign_packages(warehouses, agents, packages)

        # All 3 W1 packages assigned to A1 in order
        self.assertEqual([p["id"] for p in assignments["A1"]], ["P1", "P2", "P3"])
        # W2 package assigned to A2
        self.assertEqual([p["id"] for p in assignments["A2"]], ["P4"])

    def test_package_count_conservation(self):
        warehouses = {"W1": (0.0, 0.0), "W2": (50.0, 50.0)}
        agents = {"A1": (0.0, 0.0), "A2": (50.0, 50.0), "A3": (100.0, 100.0)}
        packages = [
            {"id": f"P{i}", "warehouse": "W1" if i % 2 == 0 else "W2", "destination": (10.0, 10.0)}
            for i in range(15)
        ]

        assignments = assign_packages(warehouses, agents, packages)
        total_assigned = sum(len(pkgs) for pkgs in assignments.values())
        self.assertEqual(total_assigned, len(packages))

        # Check that every package was assigned exactly once
        assigned_ids = [p["id"] for pkgs in assignments.values() for p in pkgs]
        self.assertEqual(sorted(assigned_ids), sorted([p["id"] for p in packages]))

    def test_agent_with_zero_packages(self):
        warehouses = {"W1": (0.0, 0.0)}
        agents = {
            "A1": (1.0, 1.0),
            "A2": (500.0, 500.0),  # Far away, receives no packages
        }
        packages = [
            {"id": "P1", "warehouse": "W1", "destination": (10.0, 10.0)}
        ]

        assignments = assign_packages(warehouses, agents, packages)
        self.assertEqual(len(assignments["A1"]), 1)
        self.assertIn("A2", assignments)
        self.assertEqual(assignments["A2"], [])

    def test_malformed_warehouse_reference(self):
        warehouses = {"W1": (0.0, 0.0)}
        agents = {"A1": (5.0, 5.0)}
        packages = [
            {"id": "P1", "warehouse": "NON_EXISTENT_W", "destination": (10.0, 10.0)}
        ]

        with self.assertRaisesRegex(ValueError, "references unknown warehouse 'NON_EXISTENT_W'"):
            assign_packages(warehouses, agents, packages)

    def test_empty_agents_or_warehouses(self):
        with self.assertRaisesRegex(ValueError, "'agents' collection is empty"):
            assign_packages({"W1": (0.0, 0.0)}, {}, [])

        with self.assertRaisesRegex(ValueError, "'warehouses' collection is empty"):
            assign_packages({}, {"A1": (0.0, 0.0)}, [])


if __name__ == "__main__":
    unittest.main()
