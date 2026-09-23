import glob
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastbox.parser import load_data, parse_data


class TestParser(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.base_case_path = os.path.join(self.root_dir, "base_case.json")
        self.test_cases_dir = os.path.join(
            self.root_dir, "Python Assignment(Delivery System Test Cases)"
        )

    def test_load_base_case_file(self):
        data = load_data(self.base_case_path)
        self.assertIn("warehouses", data)
        self.assertIn("agents", data)
        self.assertIn("packages", data)

        self.assertEqual(len(data["warehouses"]), 3)
        self.assertEqual(len(data["agents"]), 3)
        self.assertEqual(len(data["packages"]), 5)

        # Check normalization
        self.assertEqual(data["warehouses"]["W1"], (0.0, 0.0))
        self.assertEqual(data["agents"]["A1"], (5.0, 5.0))
        self.assertEqual(data["packages"][0]["id"], "P1")
        self.assertEqual(data["packages"][0]["warehouse"], "W1")
        self.assertEqual(data["packages"][0]["destination"], (30.0, 40.0))

    def test_load_all_provided_test_cases(self):
        json_files = glob.glob(os.path.join(self.test_cases_dir, "test_case_*.json"))
        self.assertGreaterEqual(len(json_files), 10)

        for filepath in json_files:
            with self.subTest(filepath=os.path.basename(filepath)):
                data = load_data(filepath)
                self.assertIsInstance(data["warehouses"], dict)
                self.assertIsInstance(data["agents"], dict)
                self.assertIsInstance(data["packages"], list)
                self.assertGreater(len(data["warehouses"]), 0)
                self.assertGreater(len(data["agents"]), 0)
                self.assertGreater(len(data["packages"]), 0)

                for pkg in data["packages"]:
                    self.assertIn("id", pkg)
                    self.assertIn("warehouse", pkg)
                    self.assertIn("destination", pkg)
                    self.assertIn(pkg["warehouse"], data["warehouses"])
                    self.assertEqual(len(pkg["destination"]), 2)

    def test_normalize_dict_format(self):
        raw = {
            "warehouses": {"W1": [10, 20]},
            "agents": {"A1": [30, 40]},
            "packages": [
                {"id": "P1", "warehouse": "W1", "destination": [50, 60]}
            ],
        }
        normalized = parse_data(raw)
        self.assertEqual(normalized["warehouses"]["W1"], (10.0, 20.0))
        self.assertEqual(normalized["agents"]["A1"], (30.0, 40.0))
        self.assertEqual(normalized["packages"][0]["warehouse"], "W1")

    def test_normalize_list_format_with_warehouse_id_key(self):
        raw = {
            "warehouses": [{"id": "W1", "location": [10, 20]}],
            "agents": [{"id": "A1", "location": [30, 40]}],
            "packages": [
                {"id": "P1", "warehouse_id": "W1", "destination": [50, 60]}
            ],
        }
        normalized = parse_data(raw)
        self.assertEqual(normalized["warehouses"]["W1"], (10.0, 20.0))
        self.assertEqual(normalized["agents"]["A1"], (30.0, 40.0))
        self.assertEqual(normalized["packages"][0]["warehouse"], "W1")

    def test_preserve_extra_package_fields(self):
        raw = {
            "warehouses": {"W1": [0, 0]},
            "agents": {"A1": [1, 1]},
            "packages": [
                {"id": "P1", "warehouse": "W1", "destination": [2, 2], "priority": "high", "weight": 2.5}
            ],
        }
        normalized = parse_data(raw)
        self.assertEqual(normalized["packages"][0]["priority"], "high")
        self.assertEqual(normalized["packages"][0]["weight"], 2.5)

    def test_missing_top_level_fields(self):
        for missing_field in ("warehouses", "agents", "packages"):
            raw = {
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [1, 1]},
                "packages": [{"id": "P1", "warehouse": "W1", "destination": [2, 2]}],
            }
            del raw[missing_field]
            with self.subTest(missing=missing_field):
                with self.assertRaisesRegex(ValueError, f"Missing required top-level field: '{missing_field}'"):
                    parse_data(raw)

    def test_non_dict_top_level(self):
        with self.assertRaisesRegex(ValueError, "Top-level JSON structure must be a dictionary"):
            parse_data(["not", "a", "dict"])

    def test_empty_collections(self):
        # Empty warehouses
        with self.assertRaisesRegex(ValueError, "'warehouse' collection cannot be empty"):
            parse_data({
                "warehouses": {},
                "agents": {"A1": [0, 0]},
                "packages": [{"id": "P1", "warehouse": "W1", "destination": [1, 1]}],
            })

        # Empty agents
        with self.assertRaisesRegex(ValueError, "'agent' collection cannot be empty"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": {},
                "packages": [{"id": "P1", "warehouse": "W1", "destination": [1, 1]}],
            })

        # Empty packages
        with self.assertRaisesRegex(ValueError, "'packages' collection cannot be empty"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [0, 0]},
                "packages": [],
            })

    def test_invalid_coordinates(self):
        invalid_coords = [
            ("single value", [10]),
            ("three values", [10, 20, 30]),
            ("string value", ["10", 20]),
            ("boolean value", [True, 20]),
            ("null value", [None, 20]),
            ("non-sequence", 42),
            ("infinite value", [float("inf"), 20]),
            ("NaN value", [float("nan"), 20]),
        ]
        for label, coord in invalid_coords:
            with self.subTest(label=label):
                raw = {
                    "warehouses": {"W1": coord},
                    "agents": {"A1": [0, 0]},
                    "packages": [{"id": "P1", "warehouse": "W1", "destination": [1, 1]}],
                }
                with self.assertRaises(ValueError):
                    parse_data(raw)

    def test_duplicate_ids(self):
        # Duplicate warehouse ID in list format
        with self.assertRaisesRegex(ValueError, "Duplicate warehouse ID: 'W1'"):
            parse_data({
                "warehouses": [
                    {"id": "W1", "location": [0, 0]},
                    {"id": "W1", "location": [10, 10]},
                ],
                "agents": {"A1": [0, 0]},
                "packages": [{"id": "P1", "warehouse": "W1", "destination": [1, 1]}],
            })

        # Duplicate agent ID in list format
        with self.assertRaisesRegex(ValueError, "Duplicate agent ID: 'A1'"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": [
                    {"id": "A1", "location": [0, 0]},
                    {"id": "A1", "location": [10, 10]},
                ],
                "packages": [{"id": "P1", "warehouse": "W1", "destination": [1, 1]}],
            })

        # Duplicate package ID
        with self.assertRaisesRegex(ValueError, "Duplicate package ID: 'P1'"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [0, 0]},
                "packages": [
                    {"id": "P1", "warehouse": "W1", "destination": [1, 1]},
                    {"id": "P1", "warehouse": "W1", "destination": [2, 2]},
                ],
            })

    def test_unknown_warehouse_reference(self):
        with self.assertRaisesRegex(ValueError, "references unknown warehouse 'W99'"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [0, 0]},
                "packages": [{"id": "P1", "warehouse": "W99", "destination": [1, 1]}],
            })

    def test_blank_or_invalid_ids(self):
        with self.assertRaisesRegex(ValueError, "Warehouse ID must be a non-empty string"):
            parse_data({
                "warehouses": {"": [0, 0]},
                "agents": {"A1": [0, 0]},
                "packages": [{"id": "P1", "warehouse": "W1", "destination": [1, 1]}],
            })

        with self.assertRaisesRegex(ValueError, "Agent ID must be a non-empty string"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": [
                    {"id": "  ", "location": [0, 0]}
                ],
                "packages": [{"id": "P1", "warehouse": "W1", "destination": [1, 1]}],
            })

        with self.assertRaisesRegex(ValueError, "Package ID must be a non-empty string"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [0, 0]},
                "packages": [{"id": "", "warehouse": "W1", "destination": [1, 1]}],
            })

    def test_missing_warehouse_reference_in_package(self):
        with self.assertRaisesRegex(ValueError, "missing valid warehouse reference"):
            parse_data({
                "warehouses": {"W1": [0, 0]},
                "agents": {"A1": [0, 0]},
                "packages": [{"id": "P1", "destination": [1, 1]}],
            })


if __name__ == "__main__":
    unittest.main()
