# AGENTS.md — Project Coding Rules

## Scope

Nexgensis Technologies Python Developer Assignment: "Mystery Delivery System" logistics simulator.

## Core Principles

- **Simplicity first.** Write straightforward Python a junior developer can explain in an interview.
- **No unnecessary infrastructure.** No frameworks, APIs, databases, Docker, or cloud services.
- **Standard library only** (`json`, `math`, `os`, `sys`, `csv`). No third-party packages required.
- **Minimal comments.** Don't comment obvious Python; document only non-obvious decisions and ambiguities.

## Input Format Handling

The assignment ships two conflicting JSON schemas. The parser must normalise both into a common internal representation.

| Element     | `base_case.json` (list-of-dicts)             | `test_case_*.json` / PDF sample (dict)  |
|-------------|----------------------------------------------|-----------------------------------------|
| warehouses  | `[{"id": "W1", "location": [0, 0]}, ...]`   | `{"W1": [0, 0], ...}`                  |
| agents      | `[{"id": "A1", "location": [5, 5]}, ...]`    | `{"A1": [5, 5], ...}`                  |
| packages    | `"warehouse_id"` key                          | `"warehouse"` key                       |

Detection: if `warehouses` value is a `list`, use list-of-dicts path; if `dict`, use dict path.

## Algorithm Rules (from PDF)

1. **Distance metric:** Euclidean distance `sqrt((x2-x1)² + (y2-y1)²)`.
2. **Assignment:** Each package is assigned to the agent nearest to that package's warehouse.
3. **Simulation:** Agent travels from current position → warehouse → destination for each assigned package, sequentially (chained delivery — agent stays at last destination).
4. **Efficiency:** `total_distance / packages_delivered` (distance per package).
5. **Best agent:** Lowest efficiency value (least distance per package).
6. **Output:** `report.json` with per-agent stats and `best_agent` field.

## Known PDF Discrepancy

The sample report in the PDF shows:
- A1: total_distance=85.32, A2: 120.12, A3: 50.00

These numbers do **not** match any consistent application of the stated rules to the PDF's own input data. Verified models:
- Chained delivery: A1=121.21, A2=79.21, A3=14.14
- Independent trips: A1=78.28, A2=72.24, A3=14.14

**Decision:** Implement the algorithm as described in the PDF's written rules (Euclidean distance, nearest-agent assignment, chained delivery). Do not reverse-engineer the sample numbers. Document this in ASSUMPTIONS.md.

## Tie-Breaking

When multiple agents are equidistant from a warehouse, assign to the agent whose ID sorts first lexicographically (e.g., "A1" before "A2"). This ensures deterministic output.

## Output Format

Round `total_distance` and `efficiency` to 2 decimal places in the report.

## File Structure

```
assignment/
├── main.py              # Entry point: load, simulate, save report
├── data.json            # Default input (copy of base_case.json in dict format)
├── report.json          # Generated output
├── README.md            # Usage instructions
├── ASSUMPTIONS.md       # Documented ambiguities and decisions
├── base_case.json       # Provided test data (list-of-dicts format)
└── Python Assignment(Delivery System Test Cases)/
    └── test_case_*.json # Provided test data (dict format)
```
