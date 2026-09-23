import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.delays import calculate_agent_delays, simulate_delays


class TestDelays(unittest.TestCase):
    def setUp(self):
        self.packages = [
            {"id": f"P{i}", "warehouse": "W1", "destination": (10.0, 10.0)}
            for i in range(1, 6)
        ]

    def test_reproducibility_with_seed(self):
        delays_run1 = simulate_delays(self.packages, seed=42)
        delays_run2 = simulate_delays(self.packages, seed=42)
        self.assertEqual(delays_run1, delays_run2)

    def test_different_seeds_vary(self):
        delays_run1 = simulate_delays(self.packages, seed=123)
        delays_run2 = simulate_delays(self.packages, seed=999)
        self.assertNotEqual(delays_run1, delays_run2)

    def test_zero_delay_probability(self):
        delays = simulate_delays(self.packages, delay_probability=0.0, seed=1)
        for pkg_id, delay in delays.items():
            self.assertEqual(delay, 0.0)

    def test_full_delay_probability_bounds(self):
        min_d, max_d = 5.0, 15.0
        delays = simulate_delays(
            self.packages,
            min_delay_mins=min_d,
            max_delay_mins=max_d,
            delay_probability=1.0,
            seed=7,
        )
        for pkg_id, delay in delays.items():
            self.assertGreaterEqual(delay, min_d)
            self.assertLessEqual(delay, max_d)

    def test_invalid_parameters_raise(self):
        with self.assertRaisesRegex(ValueError, "Invalid delay range"):
            simulate_delays(self.packages, min_delay_mins=10.0, max_delay_mins=5.0)

        with self.assertRaisesRegex(ValueError, "delay_probability must be between"):
            simulate_delays(self.packages, delay_probability=1.5)

    def test_calculate_agent_delays(self):
        assignments = {
            "A1": [{"id": "P1"}, {"id": "P2"}],
            "A2": [{"id": "P3"}, {"id": "P4"}],
            "A3": [],
        }
        package_delays = {
            "P1": 10.5,
            "P2": 0.0,
            "P3": 5.0,
            "P4": 7.2,
        }
        stats = calculate_agent_delays(assignments, package_delays)

        self.assertEqual(stats["A1"]["total_delay_mins"], 10.5)
        self.assertEqual(stats["A1"]["delayed_packages"], 1)

        self.assertEqual(stats["A2"]["total_delay_mins"], 12.2)
        self.assertEqual(stats["A2"]["delayed_packages"], 2)

        self.assertEqual(stats["A3"]["total_delay_mins"], 0.0)
        self.assertEqual(stats["A3"]["delayed_packages"], 0)


if __name__ == "__main__":
    unittest.main()
