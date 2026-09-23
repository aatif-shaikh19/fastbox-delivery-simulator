import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.mid_day import simulate_midday_join


class TestMidDay(unittest.TestCase):
    def setUp(self):
        # W1 at (0, 0), W2 at (100, 100)
        # Initial Agent A1 at (0, 0)
        # Packages P1 and P2 from W1; P3 and P4 from W2
        self.data = {
            "warehouses": {"W1": (0.0, 0.0), "W2": (100.0, 100.0)},
            "agents": {"A1": (0.0, 0.0)},
            "packages": [
                {"id": "P1", "warehouse": "W1", "destination": (5.0, 5.0)},
                {"id": "P2", "warehouse": "W1", "destination": (10.0, 10.0)},
                {"id": "P3", "warehouse": "W2", "destination": (95.0, 95.0)},
                {"id": "P4", "warehouse": "W2", "destination": (90.0, 90.0)},
            ],
        }

    def test_new_agent_receives_phase2_packages(self):
        # A_NEW joins at (100, 100), right next to W2, after 2 packages
        data_copy = copy.deepcopy(self.data)
        report = simulate_midday_join(
            data=data_copy,
            new_agent_id="A_NEW",
            new_agent_location=(100.0, 100.0),
            cutoff_package_index=2,
        )

        self.assertIn("A_NEW", report)
        self.assertIn("A1", report)

        # A1 delivered P1 and P2 (Phase 1)
        self.assertEqual(report["A1"]["packages_delivered"], 2)

        # A_NEW delivered P3 and P4 (Phase 2, closer to W2)
        self.assertEqual(report["A_NEW"]["packages_delivered"], 2)

        # Total package conservation
        self.assertEqual(
            report["A1"]["packages_delivered"] + report["A_NEW"]["packages_delivered"],
            4,
        )

    def test_cutoff_at_zero_new_agent_from_start(self):
        # New agent joins before any packages are delivered (cutoff = 0)
        report = simulate_midday_join(
            data=self.data,
            new_agent_id="A_NEW",
            new_agent_location=(100.0, 100.0),
            cutoff_package_index=0,
        )
        self.assertEqual(report["A1"]["packages_delivered"], 2)  # W1 packages
        self.assertEqual(report["A_NEW"]["packages_delivered"], 2)  # W2 packages

    def test_cutoff_at_end_new_agent_idle(self):
        # New agent joins after all 4 packages are delivered
        report = simulate_midday_join(
            data=self.data,
            new_agent_id="A_NEW",
            new_agent_location=(50.0, 50.0),
            cutoff_package_index=4,
        )
        self.assertEqual(report["A1"]["packages_delivered"], 4)
        self.assertEqual(report["A_NEW"]["packages_delivered"], 0)
        self.assertEqual(report["A_NEW"]["total_distance"], 0.0)
        self.assertEqual(report["A_NEW"]["efficiency"], 0.0)

    def test_does_not_mutate_original_input(self):
        original_agents_count = len(self.data["agents"])
        simulate_midday_join(
            data=self.data,
            new_agent_id="A_NEW",
            new_agent_location=(50.0, 50.0),
            cutoff_package_index=2,
        )
        # Original data dict must be unchanged
        self.assertEqual(len(self.data["agents"]), original_agents_count)
        self.assertNotIn("A_NEW", self.data["agents"])


if __name__ == "__main__":
    unittest.main()
