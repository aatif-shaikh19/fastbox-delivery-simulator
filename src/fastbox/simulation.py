"""
Delivery simulation and reporting logic for the FastBox delivery system.
"""

import json
import os
from typing import Any
from fastbox.assignment import assign_packages
from fastbox.distance import Point, euclidean_distance


def simulate_agent(
    start_pos: Point,
    packages: list[dict[str, Any]],
    warehouses: dict[str, Point],
) -> dict[str, Any]:
    """
    Simulate deliveries for a single agent following chained sequential delivery.

    Trip routing for each package:
      current_pos -> package warehouse -> package destination
    After delivery, the agent remains at the destination to begin the next trip.
    All calculations are performed at full floating-point precision.
    """
    current_pos = start_pos
    total_distance = 0.0

    for pkg in packages:
        w_id = pkg["warehouse"]
        w_loc = warehouses[w_id]
        dest_loc = pkg["destination"]

        # Travel: agent current position -> warehouse -> destination
        dist_to_warehouse = euclidean_distance(current_pos, w_loc)
        dist_to_destination = euclidean_distance(w_loc, dest_loc)

        total_distance += dist_to_warehouse + dist_to_destination
        current_pos = dest_loc

    delivered_count = len(packages)
    efficiency = (total_distance / delivered_count) if delivered_count > 0 else 0.0

    return {
        "packages_delivered": delivered_count,
        "total_distance": total_distance,
        "efficiency": efficiency,
    }


def simulate_deliveries(
    warehouses: dict[str, Point],
    agents: dict[str, Point],
    assignments: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """
    Simulate deliveries for all agents given their assigned packages.
    Returns unrounded full-precision statistics for each agent.
    """
    stats: dict[str, dict[str, Any]] = {}

    for agent_id in sorted(agents.keys()):
        assigned_pkgs = assignments.get(agent_id, [])
        stats[agent_id] = simulate_agent(
            start_pos=agents[agent_id],
            packages=assigned_pkgs,
            warehouses=warehouses,
        )

    return stats


def find_best_agent(agent_stats: dict[str, dict[str, Any]]) -> str | None:
    """
    Determine the best agent according to a strict deterministic rule:

    1. Eligibility: Only agents who delivered at least one package
       (packages_delivered > 0) are considered.
    2. Primary criterion: Lowest efficiency (least total distance per package delivered).
    3. Secondary tie-breaker: Highest number of packages delivered.
    4. Tertiary tie-breaker: Lexicographical order of agent ID (e.g., 'A1' before 'A2').

    Returns None if no agent delivered any packages.
    """
    eligible = [
        (aid, data)
        for aid, data in agent_stats.items()
        if data["packages_delivered"] > 0
    ]

    if not eligible:
        return None

    best = min(
        eligible,
        key=lambda item: (
            item[1]["efficiency"],
            -item[1]["packages_delivered"],
            item[0],
        ),
    )
    return best[0]


def generate_report(
    agent_stats: dict[str, dict[str, Any]],
    round_values: bool = True,
) -> dict[str, Any]:
    """
    Generate the final report structure matching the assignment specification.
    Rounds total_distance and efficiency to 2 decimal places by default.
    """
    report: dict[str, Any] = {}

    for agent_id in sorted(agent_stats.keys()):
        stats = agent_stats[agent_id]
        total_dist = stats["total_distance"]
        eff = stats["efficiency"]

        report[agent_id] = {
            "packages_delivered": stats["packages_delivered"],
            "total_distance": round(total_dist, 2) if round_values else total_dist,
            "efficiency": round(eff, 2) if round_values else eff,
        }

    report["best_agent"] = find_best_agent(agent_stats)
    return report


def run_simulation(data: dict[str, Any], round_values: bool = True) -> dict[str, Any]:
    """
    Execute full assignment pipeline: assign packages, simulate travel,
    and generate formatted report.
    """
    warehouses = data["warehouses"]
    agents = data["agents"]
    packages = data["packages"]

    assignments = assign_packages(warehouses, agents, packages)
    stats = simulate_deliveries(warehouses, agents, assignments)
    return generate_report(stats, round_values=round_values)


def save_report(report_data: dict[str, Any], filepath: str | os.PathLike) -> None:
    """Save report dictionary to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
