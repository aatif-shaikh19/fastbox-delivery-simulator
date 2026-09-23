"""
Package-to-agent assignment logic for the FastBox delivery system.
"""

from typing import Any
from fastbox.distance import Point, euclidean_distance


def find_nearest_agent(warehouse_loc: Point, agents: dict[str, Point]) -> str:
    """
    Find the agent nearest to warehouse_loc by Euclidean distance.

    Tie-breaking rule:
    When multiple agents are equidistant to a warehouse, the agent whose ID
    is lexicographically smallest is chosen (e.g., 'A1' before 'A2').
    """
    if not agents:
        raise ValueError("Cannot find nearest agent: 'agents' collection is empty")

    return min(
        agents.keys(),
        key=lambda agent_id: (
            euclidean_distance(agents[agent_id], warehouse_loc),
            agent_id,
        ),
    )


def assign_packages(
    warehouses: dict[str, Point],
    agents: dict[str, Point],
    packages: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Assign each package to the nearest agent to that package's warehouse.

    - Caches the nearest agent per warehouse since multiple packages may share a warehouse.
    - Preserves input order of packages for each agent.
    - Ensures every package is assigned exactly once.
    - Initializes entries for all known agents, even if an agent receives 0 packages.
    """
    if not agents:
        raise ValueError("Cannot assign packages: 'agents' collection is empty")
    if not warehouses:
        raise ValueError("Cannot assign packages: 'warehouses' collection is empty")

    # Validate unknown warehouse references before performing calculations
    for pkg in packages:
        w_id = pkg.get("warehouse")
        if not w_id or w_id not in warehouses:
            pkg_id = pkg.get("id", "unknown")
            raise ValueError(f"Package '{pkg_id}' references unknown warehouse '{w_id}'")

    # Initialize assignment lists for every agent in deterministic order
    assignments: dict[str, list[dict[str, Any]]] = {
        agent_id: [] for agent_id in sorted(agents.keys())
    }

    # Cache warehouse -> nearest agent to avoid redundant distance calculations
    warehouse_agent_cache: dict[str, str] = {}

    for pkg in packages:
        w_id = pkg["warehouse"]
        if w_id not in warehouse_agent_cache:
            warehouse_agent_cache[w_id] = find_nearest_agent(warehouses[w_id], agents)

        assigned_agent = warehouse_agent_cache[w_id]
        assignments[assigned_agent].append(pkg)

    return assignments
