import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.export import CSV_HEADER, export_top_performer_to_csv


class TestExport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_successful_top_performer(self):
        report = {
            "A1": {"packages_delivered": 2, "total_distance": 121.21, "efficiency": 60.61},
            "A3": {"packages_delivered": 1, "total_distance": 14.14, "efficiency": 14.14},
            "best_agent": "A3",
        }
        csv_path = os.path.join(self.temp_dir.name, "top_performer.csv")
        result = export_top_performer_to_csv(report, csv_path)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_path))

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = list(csv.reader(f))

        self.assertEqual(len(reader), 2)
        self.assertEqual(reader[0], CSV_HEADER)
        self.assertEqual(reader[1], ["A3", "1", "14.14", "14.14"])

    def test_export_no_deliveries_edge_case(self):
        report = {
            "A1": {"packages_delivered": 0, "total_distance": 0.0, "efficiency": 0.0},
            "best_agent": None,
        }
        csv_path = os.path.join(self.temp_dir.name, "no_performer.csv")
        result = export_top_performer_to_csv(report, csv_path)

        self.assertFalse(result)
        self.assertTrue(os.path.exists(csv_path))

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = list(csv.reader(f))

        # Only header row should be written
        self.assertEqual(len(reader), 1)
        self.assertEqual(reader[0], CSV_HEADER)


if __name__ == "__main__":
    unittest.main()
