"""
Bonus 3: Top Performer CSV Export.

Exports the best performing agent's summary to a CSV file.
"""

import csv
import os
from typing import Any

CSV_HEADER = ["agent_id", "packages_delivered", "total_distance", "efficiency"]


def export_top_performer_to_csv(
    report: dict[str, Any],
    filepath: str | os.PathLike = "top_performer.csv",
) -> bool:
    """
    Write the best agent's performance metrics to a CSV file.

    Args:
        report: Final report dictionary (containing agent keys and 'best_agent').
        filepath: Destination CSV file path.

    Returns:
        True if a top performer was written; False if no best agent was found.
    """
    best_agent_id = report.get("best_agent")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

        if best_agent_id and best_agent_id in report:
            stats = report[best_agent_id]
            writer.writerow([
                best_agent_id,
                stats["packages_delivered"],
                stats["total_distance"],
                stats["efficiency"],
            ])
            return True

    return False
