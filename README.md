# FastBox Delivery System Simulator

A lightweight, robust logistics simulator designed for **FastBox**, simulating a day of operations across multiple warehouses, delivery agents, and packages.

Built for the **Nexgensis Technologies Python Developer Assignment** with simplicity, clarity, and standard library principles.

---

## Features

- **Dual-Format JSON Normalization:** Seamlessly loads and normalizes both `list-of-dicts` (`base_case.json`) and `dict` schemas (`test_case_*.json`).
- **Nearest-Agent Package Assignment:** Evaluates Euclidean distance from agent start positions to warehouses with deterministic tie-breaking and per-warehouse result caching.
- **Chained Sequential Simulation:** Models real-world sequential delivery trips where an agent travels `current_position -> warehouse -> destination`, remaining at the destination for subsequent pickups.
- **Full-Precision Internals:** Preserves complete floating-point accuracy during travel simulation, rounding metrics (`total_distance`, `efficiency`) only when generating `report.json`.
- **Zero Third-Party Runtime Dependencies:** 100% standard library (`math`, `json`, `os`, `sys`, `csv`, `random`).
- **All 4 Assignment Bonuses Implemented:**
  1. *Random Delivery Delays* (`src/fastbox/delays.py`)
  2. *2D ASCII Map Visualization* (`src/fastbox/visualization.py`)
  3. *Top Performer CSV Export* (`src/fastbox/export.py`)
  4. *Mid-Day Dynamic Agent Joining* (`src/fastbox/mid_day.py`)

---

## Project Structure

```text
assignment/
├── src/
│   └── fastbox/
│       ├── __init__.py           # Package exports
│       ├── distance.py           # 2D Euclidean distance calculation
│       ├── parser.py             # Schema normalization and strict validation
│       ├── assignment.py         # Nearest-agent mapping with warehouse caching
│       ├── simulation.py         # Chained trip simulation and report generation
│       ├── delays.py             # Bonus 1: Reproducible delivery delay simulation
│       ├── visualization.py      # Bonus 2: 2D ASCII grid rendering
│       ├── export.py             # Bonus 3: Top performer CSV export
│       └── mid_day.py            # Bonus 4: Mid-day dynamic fleet expansion
├── tests/
│   ├── __init__.py
│   ├── test_distance.py          # Distance metric unit tests
│   ├── test_parser.py            # Schema normalization and validation tests
│   ├── test_assignment.py        # Assignment and tie-breaking tests
│   ├── test_simulation.py        # Chained delivery and best-agent tests
│   ├── test_delays.py            # Delivery delays unit tests
│   ├── test_visualization.py     # ASCII visualization unit tests
│   ├── test_export.py            # CSV export unit tests
│   └── test_mid_day.py           # Mid-day join unit tests
├── Python Assignment(Delivery System Test Cases)/
│   └── test_case_*.json          # 10 provided evaluation test cases
├── main.py                       # CLI entry point
├── data.json                     # Default assignment input (dict format)
├── base_case.json                # Base test case (list format)
├── report.json                   # Generated simulation report
├── top_performer.csv             # Exported best agent summary
├── requirements.txt              # Dependency specification (std-lib runtime)
├── ASSUMPTIONS.md                # Documented design decisions & discrepancy analysis
├── AGENTS.md                     # Project coding rules
└── .gitignore                    # Python cache and artifact ignore rules
```

---

## Getting Started

### Prerequisites

- **Python 3.10+** (Tested on Python 3.11.9)
- No third-party packages are required to run the simulation.

Optional: To use `pytest` as the test runner:
```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Basic Execution (Core Assignment)

Run the simulation on the default input file (`data.json` or `base_case.json`):

```bash
python main.py
```

Run on a specific input file:

```bash
# Run on base case:
python main.py base_case.json

# Run on any provided test case:
python main.py "Python Assignment(Delivery System Test Cases)/test_case_1.json"
```

Specify a custom report output path:

```bash
python main.py base_case.json custom_report.json
```

### 2. Running with Optional Bonus Features

Enable optional bonus features via CLI flags:

```bash
# Enable ASCII map visualization:
python main.py base_case.json --ascii

# Export top performer to CSV:
python main.py base_case.json --export-csv

# Simulate delivery delays:
python main.py base_case.json --delays

# Run all bonus features simultaneously:
python main.py base_case.json report.json --ascii --export-csv --delays
```

---

## Running Tests

Run the complete test suite (49 unit tests) with Python's built-in test runner:

```bash
python -m unittest discover tests
```

Or using `pytest`:

```bash
python -m pytest -v
```

---

## Key Design Decisions & Verified Discrepancy

1. **PDF Sample Numbers Discrepancy:**
   The illustrative sample report in the PDF (`A1: 85.32, A2: 120.12, A3: 50.00`) does not match Euclidean travel under either chained delivery or independent trips for the provided coordinates. In accordance with hiring assignment best practices, the written routing rules are implemented directly. See [ASSUMPTIONS.md](file:///c:/Users/Aatif/Downloads/assignment/ASSUMPTIONS.md) for full mathematical verification.

2. **Deterministic Tie-Breaking:**
   - For equidistant agents to a warehouse, the agent whose ID sorts first lexicographically (e.g., `"A1"` before `"A2"`) is selected.
   - For `best_agent`, only agents with `packages_delivered > 0` are eligible; lowest efficiency wins, with higher package volume as secondary tie-breaker.

3. **Validation:**
   Inputs are validated against missing keys, malformed or boolean coordinates, unknown warehouse references, and duplicate entity IDs, raising informative `ValueError` exceptions.
