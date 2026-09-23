"""
Bonus 2: ASCII Visualization for the FastBox delivery system.

Renders a 2D text-based grid showing warehouses, agent starting positions,
and package destinations with normalized coordinate scaling and a legend.
"""

from typing import Any
from fastbox.distance import Point


def render_ascii_map(
    data: dict[str, Any],
    grid_width: int = 40,
    grid_height: int = 15,
) -> str:
    """
    Render warehouses, agent start positions, and package destinations
    on a normalized ASCII grid.

    Entities:
      W = Warehouse
      A = Agent Start
      P = Package Destination
      * = Overlapping entities

    Returns:
        Formatted multi-line string containing the border, grid, and legend.
    """
    warehouses: dict[str, Point] = data.get("warehouses", {})
    agents: dict[str, Point] = data.get("agents", {})
    packages: list[dict[str, Any]] = data.get("packages", [])

    all_points: list[Point] = (
        list(warehouses.values())
        + list(agents.values())
        + [pkg["destination"] for pkg in packages if "destination" in pkg]
    )

    if not all_points:
        return "ASCII Map: No coordinate data available to render.\n"

    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = (max_x - min_x) if max_x > min_x else 1.0
    span_y = (max_y - min_y) if max_y > min_y else 1.0

    def to_grid(x: float, y: float) -> tuple[int, int]:
        col = int(round((x - min_x) / span_x * (grid_width - 1)))
        # Invert row so higher Y coordinates are printed near the top
        row = int(round((max_y - y) / span_y * (grid_height - 1)))
        col = max(0, min(grid_width - 1, col))
        row = max(0, min(grid_height - 1, row))
        return col, row

    # Initialize empty grid
    grid = [["." for _ in range(grid_width)] for _ in range(grid_height)]

    def place_marker(col: int, row: int, char: str) -> None:
        current = grid[row][col]
        if current == ".":
            grid[row][col] = char
        elif current != char:
            grid[row][col] = "*"  # Mark collision

    # Place packages destinations first
    for pkg in packages:
        if "destination" in pkg:
            c, r = to_grid(pkg["destination"][0], pkg["destination"][1])
            place_marker(c, r, "P")

    # Place agents
    for aid, pos in agents.items():
        c, r = to_grid(pos[0], pos[1])
        place_marker(c, r, "A")

    # Place warehouses
    for wid, pos in warehouses.items():
        c, r = to_grid(pos[0], pos[1])
        place_marker(c, r, "W")

    # Build ASCII output
    lines = [
        f"FastBox Simulation Map (X: [{min_x:.0f}..{max_x:.0f}], Y: [{min_y:.0f}..{max_y:.0f}])",
        "+" + "-" * grid_width + "+",
    ]
    for row in grid:
        lines.append("|" + "".join(row) + "|")
    lines.append("+" + "-" * grid_width + "+")

    # Add legend
    lines.extend([
        "Legend:",
        "  W : Warehouse",
        "  A : Agent Start Position",
        "  P : Package Destination",
        "  * : Overlapping Entities",
        "  . : Empty Space",
    ])

    return "\n".join(lines) + "\n"
