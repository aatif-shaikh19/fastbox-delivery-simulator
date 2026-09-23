"""
FastBox Mystery Delivery System — Command-line entry point.

Usage:
    python main.py [input_file.json] [output_file.json] [options]

Options:
    --ascii         Print 2D ASCII visualization of warehouses, agents, and destinations.
    --export-csv    Export the top performing agent's summary to top_performer.csv.
    --delays        Simulate and print package delivery delays (Bonus 1).

Defaults:
    input_file:  base_case.json (or data.json if present)
    output_file: report.json
"""

import json
import os
import sys

# Ensure src/ is on Python search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from fastbox.assignment import assign_packages
from fastbox.delays import calculate_agent_delays, simulate_delays
from fastbox.export import export_top_performer_to_csv
from fastbox.parser import load_data
from fastbox.simulation import run_simulation, save_report
from fastbox.visualization import render_ascii_map


def resolve_default_input() -> str:
    """Choose default input file (data.json if it exists, otherwise base_case.json)."""
    if os.path.exists("data.json"):
        return "data.json"
    return "base_case.json"


def main() -> int:
    args = sys.argv[1:]
    flags = {arg for arg in args if arg.startswith("--")}
    positional = [arg for arg in args if not arg.startswith("--")]

    input_path = positional[0] if len(positional) > 0 else resolve_default_input()
    output_path = positional[1] if len(positional) > 1 else "report.json"

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

    # Core assignment simulation
    report = run_simulation(data, round_values=True)
    save_report(report, output_path)

    print(f"\nSimulation Report successfully saved to: {output_path}")
    print(json.dumps(report, indent=4))
    print(f"\nBest performing agent: {report.get('best_agent')}")

    # Optional Bonus: ASCII Visualization
    if "--ascii" in flags:
        print("\n" + "=" * 50)
        print("BONUS: 2D ASCII Visualization")
        print("=" * 50)
        print(render_ascii_map(data))

    # Optional Bonus: CSV Export
    if "--export-csv" in flags:
        csv_filename = "top_performer.csv"
        exported = export_top_performer_to_csv(report, csv_filename)
        if exported:
            print(f"\n[Bonus] Top performer exported to: {csv_filename}")

    # Optional Bonus: Delivery Delays
    if "--delays" in flags:
        print("\n" + "=" * 50)
        print("BONUS: Delivery Delays Simulation (Seed: 42)")
        print("=" * 50)
        package_delays = simulate_delays(data["packages"], seed=42)
        assignments = assign_packages(data["warehouses"], data["agents"], data["packages"])
        agent_delays = calculate_agent_delays(assignments, package_delays)
        for aid, dstats in agent_delays.items():
            print(
                f"Agent {aid}: {dstats['delayed_packages']} delayed packages, "
                f"total delay = {dstats['total_delay_mins']} mins"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
