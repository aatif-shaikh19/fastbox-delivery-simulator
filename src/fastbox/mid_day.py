"""
Bonus 4: Mid-Day / New Agent Support.

Handles the operational scenario where a new delivery agent joins the fleet
mid-day after an initial batch of packages has already been assigned and delivered.

Design & Assumptions:
1. Operations are partitioned into two phases:
   - Phase 1 (Morning): Packages up to cutoff_index are assigned to the original
     agents and delivered. Agents end at their respective last delivery locations.
   - Phase 2 (Afternoon / Mid-Day Join): A new agent joins at a specified location.
     The remaining packages (from cutoff_index onward) are assigned using the
     expanded agent pool.
2. If the new agent is closer to a warehouse than the original agents, packages from
   that warehouse in Phase 2 are routed to the new agent.
3. Total distance and package counts are combined across both phases to produce
   the overall end-of-day performance report.
"""

from typing import Any
from fastbox.assignment import assign_packages
from fastbox.distance import Point, euclidean_distance
from fastbox.simulation import generate_report


def simulate_agent_chained(
    start_pos: Point,
    packages: list[dict[str, Any]],
    warehouses: dict[str, Point],
) -> tuple[float, Point]:
    """
    Simulate sequential deliveries for an agent.
    Returns (distance_traveled, final_agent_position).
    """
    current_pos = start_pos
    distance = 0.0

    for pkg in packages:
        w_loc = warehouses[pkg["warehouse"]]
        dest_loc = pkg["destination"]
        distance += euclidean_distance(current_pos, w_loc) + euclidean_distance(w_loc, dest_loc)
        current_pos = dest_loc

    return distance, current_pos


def simulate_midday_join(
    data: dict[str, Any],
    new_agent_id: str,
    new_agent_location: Point,
    cutoff_package_index: int,
) -> dict[str, Any]:
    """
    Simulate operations when a new agent joins after cutoff_package_index packages.

    Args:
        data: Normalized delivery data (warehouses, agents, packages).
        new_agent_id: Identifier for the joining agent (e.g., 'A_NEW').
        new_agent_location: Starting (x, y) coordinates of the new agent.
        cutoff_package_index: Number of packages already processed before the agent joins.

    Returns:
        Consolidated report dictionary including the new agent.
    """
    warehouses = data["warehouses"]
    initial_agents = dict(data["agents"])
    packages = data["packages"]

    total_packages = len(packages)
    cutoff = max(0, min(cutoff_package_index, total_packages))

    phase1_packages = packages[:cutoff]
    phase2_packages = packages[cutoff:]

    # Phase 1: Assign and simulate initial packages
    agent_positions = dict(initial_agents)
    agent_totals: dict[str, dict[str, Any]] = {
        aid: {"packages_delivered": 0, "total_distance": 0.0}
        for aid in initial_agents
    }

    if phase1_packages:
        phase1_assignments = assign_packages(warehouses, initial_agents, phase1_packages)
        for aid, pkgs in phase1_assignments.items():
            dist, end_pos = simulate_agent_chained(agent_positions[aid], pkgs, warehouses)
            agent_totals[aid]["packages_delivered"] += len(pkgs)
            agent_totals[aid]["total_distance"] += dist
            agent_positions[aid] = end_pos

    # Mid-Day Event: New agent joins
    all_agents_phase2 = dict(initial_agents)
    all_agents_phase2[new_agent_id] = new_agent_location

    agent_totals[new_agent_id] = {"packages_delivered": 0, "total_distance": 0.0}
    agent_positions[new_agent_id] = new_agent_location

    # Phase 2: Assign remaining packages with expanded agent pool
    if phase2_packages:
        phase2_assignments = assign_packages(warehouses, all_agents_phase2, phase2_packages)
        for aid, pkgs in phase2_assignments.items():
            dist, end_pos = simulate_agent_chained(agent_positions[aid], pkgs, warehouses)
            agent_totals[aid]["packages_delivered"] += len(pkgs)
            agent_totals[aid]["total_distance"] += dist
            agent_positions[aid] = end_pos

    # Calculate final efficiencies
    combined_stats: dict[str, dict[str, Any]] = {}
    for aid, stats in agent_totals.items():
        delivered = stats["packages_delivered"]
        dist = stats["total_distance"]
        eff = (dist / delivered) if delivered > 0 else 0.0
        combined_stats[aid] = {
            "packages_delivered": delivered,
            "total_distance": dist,
            "efficiency": eff,
        }

    return generate_report(combined_stats, round_values=True)
