"""
FastBox Mystery Delivery System simulator.
"""

from fastbox.assignment import assign_packages, find_nearest_agent
from fastbox.delays import calculate_agent_delays, simulate_delays
from fastbox.distance import euclidean_distance
from fastbox.export import export_top_performer_to_csv
from fastbox.mid_day import simulate_midday_join
from fastbox.parser import load_data, parse_data
from fastbox.simulation import (
    find_best_agent,
    generate_report,
    run_simulation,
    save_report,
    simulate_agent,
    simulate_deliveries,
)
from fastbox.visualization import render_ascii_map

__all__ = [
    # Core
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
    # Bonuses
    "calculate_agent_delays",
    "export_top_performer_to_csv",
    "render_ascii_map",
    "simulate_delays",
    "simulate_midday_join",
]
