"""
FastBox Mystery Delivery System — Command-line entry point.

Usage:
    python main.py [input_file.json] [output_file.json]

Defaults:
    input_file:  base_case.json (or data.json if present)
    output_file: report.json
"""

import json
import os
import sys

# Ensure src/ is on Python search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from fastbox.parser import load_data
from fastbox.simulation import run_simulation, save_report


def resolve_default_input() -> str:
    """Choose default input file (data.json if it exists, otherwise base_case.json)."""
    if os.path.exists("data.json"):
        return "data.json"
    return "base_case.json"


def main() -> int:
    input_path = sys.argv[1] if len(sys.argv) > 1 else resolve_default_input()
    output_path = sys.argv[2] if len(sys.argv) > 2 else "report.json"

    print(f"Loading input data from: {input_path}")
    try:
        data = load_data(input_path)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Validation Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Parsed {len(data['warehouses'])} warehouses, "
        f"{len(data['agents'])} agents, "
        f"{len(data['packages'])} packages."
    )

    report = run_simulation(data, round_values=True)
    save_report(report, output_path)

    print(f"\nSimulation Report successfully saved to: {output_path}")
    print(json.dumps(report, indent=4))
    print(f"\nBest performing agent: {report.get('best_agent')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
