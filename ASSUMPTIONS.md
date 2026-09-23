# ASSUMPTIONS.md — Ambiguities and Interpretations

This document records the actual ambiguities encountered in the assignment specification and the explicit interpretations adopted in our implementation.

---

### 1. Two Conflicting JSON Schemas in Supplied Files

- **Ambiguity:**
  The assignment materials provide two incompatible input schemas:
  - `base_case.json` represents `warehouses` and `agents` as lists of objects (e.g., `[{"id": "W1", "location": [0, 0]}]`) and packages using the key `"warehouse_id"`.
  - The PDF sample and all 10 files in `Python Assignment(Delivery System Test Cases)/` represent `warehouses` and `agents` as key-value mappings (e.g., `{"W1": [0, 0]}`) and packages using the key `"warehouse"`.
- **Our Interpretation:**
  The parser does not assume a single format. It inspects whether `warehouses` is a `list` or `dict`, parses both paths into a uniform internal representation (`dict[str, tuple[float, float]]`), and normalizes package warehouse references to `"warehouse"`.

---

### 2. Deterministic Tie-Breaking

- **Ambiguity:**
  The assignment states: *"Assign each package to the nearest agent based on Euclidean distance from agent to warehouse"* and *"best agent: lowest efficiency value"*. It does not specify what to do when distances or efficiencies are identical.
- **Our Interpretation:**
  - **Warehouse to Agent:** If multiple agents are equidistant to a warehouse, the agent whose ID sorts first lexicographically (e.g., `"A1"` before `"A2"`) is selected:
    ```python
    min(agents.keys(), key=lambda aid: (euclidean_distance(agents[aid], warehouse_loc), aid))
    ```
  - **Best Agent:** If multiple agents have the same minimum efficiency, tie-breaking favors the agent with the highest package count (`packages_delivered`). If still tied, the lexicographical agent ID breaks the tie.

---

### 3. Package Processing Order

- **Ambiguity:**
  When an agent is assigned multiple packages, the PDF does not state whether packages should be reordered (e.g., via Travelling Salesperson Problem / TSP optimization) or delivered in input sequence.
- **Our Interpretation:**
  Packages assigned to an agent are serviced strictly in their original input order as listed in the JSON file. No route optimization or reordering is applied, keeping the implementation simple, predictable, and aligned with standard logistics simulator requirements.

---

### 4. One-Package-at-a-Time Chained Delivery

- **Ambiguity:**
  The PDF states: *"agent picks up packages from warehouse and delivers to destination. Compute total distance traveled."* It leaves ambiguous whether an agent can carry multiple packages in one batch or must complete individual trips sequentially.
- **Our Interpretation:**
  We adopt sequential chained delivery:
  1. The agent travels from their current location to the package's warehouse.
  2. The agent travels from the warehouse to the package's destination.
  3. The agent remains at that destination, which serves as the starting point for the next trip.
  Vehicles do not batch multiple deliveries in a single run or return to their depot unless their next pickup happens to be there.

---

### 5. Handling Agents with Zero Deliveries

- **Ambiguity:**
  If an agent is never the nearest agent to any warehouse, they receive 0 packages. The efficiency formula $\frac{\text{total\_distance}}{\text{packages\_delivered}}$ would result in a division by zero. Furthermore, a naive minimum check might mistakenly select an idle agent (efficiency $0.0$) as the "best agent".
- **Our Interpretation:**
  - For agents with 0 deliveries, `packages_delivered = 0`, `total_distance = 0.0`, and `efficiency = 0.0`.
  - For `best_agent` selection, only agents that delivered at least one package (`packages_delivered > 0`) are eligible. An idle agent is never chosen over active delivery agents. If all agents delivered 0 packages, `best_agent` evaluates to `None`.

---

### 6. PDF Illustrative Distance Values Discrepancy

- **Ambiguity:**
  The sample report displayed in the assignment PDF shows:
  - `A1`: `packages_delivered = 2`, `total_distance = 85.32`, `efficiency = 42.66`
  - `A2`: `packages_delivered = 2`, `total_distance = 120.12`, `efficiency = 60.06`
  - `A3`: `packages_delivered = 1`, `total_distance = 50.00`, `efficiency = 50.00`
  - `best_agent = "A1"`

  These figures do not match the Euclidean distance calculations on the PDF's own input coordinates under any consistent model.
- **Mathematical Analysis:**
  Given:
  - `W1: [0, 0]`, `W2: [50, 75]`, `W3: [100, 25]`
  - `A1: [5, 5]`, `A2: [60, 60]`, `A3: [95, 30]`
  - `P1`: W1 $\to$ [30, 40], `P2`: W2 $\to$ [70, 90], `P3`: W3 $\to$ [105, 20], `P4`: W1 $\to$ [10, 10], `P5`: W2 $\to$ [40, 80]

  Nearest agent assignments: `A1 -> [P1, P4]`, `A2 -> [P2, P5]`, `A3 -> [P3]`.

  Under the stated chained delivery algorithm:
  - **A1:** $(5, 5) \to W1(0, 0) \to (30, 40) \to W1(0, 0) \to (10, 10)$
    $$= 7.071 + 50.000 + 50.000 + 14.142 = \mathbf{121.21}$$
  - **A2:** $(60, 60) \to W2(50, 75) \to (70, 90) \to W2(50, 75) \to (40, 80)$
    $$= 18.028 + 25.000 + 25.000 + 11.180 = \mathbf{79.21}$$
  - **A3:** $(95, 30) \to W3(100, 25) \to (105, 20)$
    $$= 7.071 + 7.071 = \mathbf{14.14}$$

  Under an independent return-to-base model:
  - `A1`: $57.071 + 21.213 = \mathbf{78.28}$
  - `A2`: $43.028 + 29.208 = \mathbf{72.24}$
  - `A3`: $\mathbf{14.14}$

- **Our Interpretation:**
  We implement the algorithm as written in the problem description (Euclidean distance, nearest-agent mapping, sequential chained delivery). We do not reverse-engineer or hardcode artificial values to match the illustrative sample report. Under actual Euclidean calculations, Agent `A3` achieves the lowest distance per package ($14.14$) and is selected as `best_agent`.

---

### 7. Assumptions for Mid-Day Agent Join Bonus

- **Ambiguity:**
  The assignment lists *"Handle new agent joining mid-day"* under optional bonuses without providing a schema or behavioral specification.
- **Our Interpretation:**
  We model a two-phase operational day:
  1. **Phase 1 (Morning):** Packages up to a specified `cutoff_package_index` are assigned to the initial agent fleet and delivered sequentially. Agents finish at their last delivery coordinates.
  2. **Phase 2 (Afternoon / Join):** A new agent joins at a specified location. Remaining packages (from the cutoff onward) are assigned using the expanded fleet (`initial_agents + new_agent`).
  3. Total distance and package counts from both phases are combined to generate end-of-day metrics for all agents.
  This ensures existing test cases remain 100% unaffected while providing a clean, realistic model for dynamic fleet expansion.
