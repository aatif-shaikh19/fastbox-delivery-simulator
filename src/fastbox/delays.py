"""
Bonus 1: Random delivery delays simulation.

Simulates traffic or customer handover delays (in minutes) independently
from the physical Euclidean travel distance.
"""

import random
from typing import Any


def simulate_delays(
    packages: list[dict[str, Any]],
    min_delay_mins: float = 2.0,
    max_delay_mins: float = 20.0,
    delay_probability: float = 0.5,
    seed: int | None = None,
) -> dict[str, float]:
    """
    Simulate delivery delays (in minutes) for each package.

    Args:
        packages: Collection of package dicts.
        min_delay_mins: Minimum delay duration when a delay occurs.
        max_delay_mins: Maximum delay duration when a delay occurs.
        delay_probability: Chance of a package experiencing a delay (0.0 - 1.0).
        seed: Optional integer seed for reproducible simulations.

    Returns:
        Dictionary mapping package_id to delay in minutes (0.0 if on time).
    """
    if min_delay_mins < 0 or max_delay_mins < min_delay_mins:
        raise ValueError("Invalid delay range: min_delay must be non-negative and <= max_delay")
    if not (0.0 <= delay_probability <= 1.0):
        raise ValueError("delay_probability must be between 0.0 and 1.0")

    rng = random.Random(seed)
    delays: dict[str, float] = {}

    for pkg in packages:
        pkg_id = pkg.get("id", "unknown")
        if rng.random() < delay_probability:
            delay = round(rng.uniform(min_delay_mins, max_delay_mins), 1)
        else:
            delay = 0.0
        delays[pkg_id] = delay

    return delays


def calculate_agent_delays(
    assignments: dict[str, list[dict[str, Any]]],
    package_delays: dict[str, float],
) -> dict[str, dict[str, Any]]:
    """
    Aggregate delay metrics per agent.

    Returns:
        {agent_id: {'total_delay_mins': float, 'delayed_packages': int}}
    """
    agent_delay_stats: dict[str, dict[str, Any]] = {}

    for agent_id, pkgs in sorted(assignments.items()):
        total_delay = sum(package_delays.get(p["id"], 0.0) for p in pkgs)
        delayed_count = sum(1 for p in pkgs if package_delays.get(p["id"], 0.0) > 0.0)
        agent_delay_stats[agent_id] = {
            "total_delay_mins": round(total_delay, 1),
            "delayed_packages": delayed_count,
        }

    return agent_delay_stats
