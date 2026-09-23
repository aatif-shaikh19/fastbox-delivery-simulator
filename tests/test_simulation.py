import glob
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.parser import load_data
from fastbox.simulation import (
    find_best_agent,
    generate_report,
    run_simulation,
    simulate_agent,
    simulate_deliveries,
)


class TestSimulation(unittest.TestCase):
    def test_single_package_delivery(self):
        warehouses = {"W1": (0.0, 0.0)}
        packages = [{"id": "P1", "warehouse": "W1", "destination": (30.0, 40.0)}]
        start_pos = (5.0, 5.0)

        # Dist from (5,5) to (0,0) is sqrt(50) = 7.0710678...
        # Dist from (0,0) to (30,40) is 50.0
        # Total dist = 57.0710678...
        stats = simulate_agent(start_pos, packages, warehouses)
        expected_distance = math.sqrt(50) + 50.0

        self.assertEqual(stats["packages_delivered"], 1)
        self.assertAlmostEqual(stats["total_distance"], expected_distance, places=6)
        self.assertAlmostEqual(stats["efficiency"], expected_distance, places=6)

    def test_multiple_sequential_deliveries_chained(self):
        """
        Verify that sequential deliveries are chained:
        Trip 1: start (5, 5) -> W1 (0, 0) -> dest1 (30, 40)
        Trip 2: dest1 (30, 40) -> W1 (0, 0) -> dest2 (10, 10)
        """
        warehouses = {"W1": (0.0, 0.0)}
        packages = [
            {"id": "P1", "warehouse": "W1", "destination": (30.0, 40.0)},
            {"id": "P4", "warehouse": "W1", "destination": (10.0, 10.0)},
        ]
        start_pos = (5.0, 5.0)

        stats = simulate_agent(start_pos, packages, warehouses)

        # Leg 1: (5,5) -> (0,0) = sqrt(50)
        # Leg 2: (0,0) -> (30,40) = 50.0
        # Leg 3: (30,40) -> (0,0) = 50.0
        # Leg 4: (0,0) -> (10,10) = sqrt(200)
        expected_dist = math.sqrt(50) + 50.0 + 50.0 + math.sqrt(200)

        self.assertEqual(stats["packages_delivered"], 2)
        self.assertAlmostEqual(stats["total_distance"], expected_dist, places=6)
        self.assertAlmostEqual(stats["efficiency"], expected_dist / 2, places=6)
        self.assertEqual(round(stats["total_distance"], 2), 121.21)

    def test_agent_with_zero_deliveries(self):
        warehouses = {"W1": (0.0, 0.0)}
        stats = simulate_agent(start_pos=(10.0, 10.0), packages=[], warehouses=warehouses)

        self.assertEqual(stats["packages_delivered"], 0)
        self.assertEqual(stats["total_distance"], 0.0)
        self.assertEqual(stats["efficiency"], 0.0)

    def test_best_agent_selection(self):
        # A1 delivered 2 pkgs with total_dist 100 -> eff 50.0
        # A2 delivered 1 pkg with total_dist 30 -> eff 30.0
        # A3 delivered 0 pkgs -> eff 0.0
        stats = {
            "A1": {"packages_delivered": 2, "total_distance": 100.0, "efficiency": 50.0},
            "A2": {"packages_delivered": 1, "total_distance": 30.0, "efficiency": 30.0},
            "A3": {"packages_delivered": 0, "total_distance": 0.0, "efficiency": 0.0},
        }

        # A2 has lowest efficiency among active agents
        self.assertEqual(find_best_agent(stats), "A2")

    def test_best_agent_ignores_idle_agents(self):
        # An agent with 0 deliveries (efficiency 0.0) must never be chosen as best agent
        stats = {
            "A1": {"packages_delivered": 0, "total_distance": 0.0, "efficiency": 0.0},
            "A2": {"packages_delivered": 1, "total_distance": 40.0, "efficiency": 40.0},
        }
        self.assertEqual(find_best_agent(stats), "A2")

        # If all agents are idle, return None
        idle_stats = {
            "A1": {"packages_delivered": 0, "total_distance": 0.0, "efficiency": 0.0},
            "A2": {"packages_delivered": 0, "total_distance": 0.0, "efficiency": 0.0},
        }
        self.assertIsNone(find_best_agent(idle_stats))

    def test_best_agent_tie_breaking(self):
        # Tie in efficiency: prefer agent with more packages delivered
        stats_tie_pkgs = {
            "A1": {"packages_delivered": 1, "total_distance": 20.0, "efficiency": 20.0},
            "A2": {"packages_delivered": 2, "total_distance": 40.0, "efficiency": 20.0},
        }
        self.assertEqual(find_best_agent(stats_tie_pkgs), "A2")

        # Exact tie in efficiency and package count: lexicographical agent ID
        stats_tie_all = {
            "A2": {"packages_delivered": 1, "total_distance": 20.0, "efficiency": 20.0},
            "A1": {"packages_delivered": 1, "total_distance": 20.0, "efficiency": 20.0},
        }
        self.assertEqual(find_best_agent(stats_tie_all), "A1")

    def test_base_case_simulation_end_to_end(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        base_case_path = os.path.join(root_dir, "base_case.json")

        data = load_data(base_case_path)
        report = run_simulation(data, round_values=True)

        self.assertIn("A1", report)
        self.assertIn("A2", report)
        self.assertIn("A3", report)
        self.assertIn("best_agent", report)

        # Verified mathematical results for chained delivery on base_case.json
        self.assertEqual(report["A1"]["packages_delivered"], 2)
        self.assertEqual(report["A1"]["total_distance"], 121.21)
        self.assertEqual(report["A1"]["efficiency"], 60.61)

        self.assertEqual(report["A2"]["packages_delivered"], 2)
        self.assertEqual(report["A2"]["total_distance"], 79.21)
        self.assertEqual(report["A2"]["efficiency"], 39.60)

        self.assertEqual(report["A3"]["packages_delivered"], 1)
        self.assertEqual(report["A3"]["total_distance"], 14.14)
        self.assertEqual(report["A3"]["efficiency"], 14.14)

        # Under the written rules, A3 traveled least distance per package
        self.assertEqual(report["best_agent"], "A3")

    def test_all_provided_test_cases_run_successfully(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        test_cases_dir = os.path.join(root_dir, "Python Assignment(Delivery System Test Cases)")
        json_files = glob.glob(os.path.join(test_cases_dir, "test_case_*.json"))

        for filepath in json_files:
            with self.subTest(filepath=os.path.basename(filepath)):
                data = load_data(filepath)
                report = run_simulation(data, round_values=True)

                total_delivered = sum(
                    report[aid]["packages_delivered"]
                    for aid in data["agents"]
                )
                self.assertEqual(total_delivered, len(data["packages"]))

                for aid in data["agents"]:
                    self.assertGreaterEqual(report[aid]["total_distance"], 0.0)
                    self.assertGreaterEqual(report[aid]["efficiency"], 0.0)

                self.assertIn(report["best_agent"], data["agents"])


if __name__ == "__main__":
    unittest.main()
