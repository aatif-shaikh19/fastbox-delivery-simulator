"""
FastBox Mystery Delivery System simulator.
"""

from fastbox.assignment import assign_packages, find_nearest_agent
from fastbox.distance import euclidean_distance
from fastbox.parser import load_data, parse_data
from fastbox.simulation import (
    find_best_agent,
    generate_report,
    run_simulation,
    save_report,
    simulate_agent,
    simulate_deliveries,
)

__all__ = [
    "assign_packages",
    "euclidean_distance",
    "find_best_agent",
    "find_nearest_agent",
    "generate_report",
    "load_data",
    "parse_data",
    "run_simulation",
    "save_report",
    "simulate_agent",
    "simulate_deliveries",
]
