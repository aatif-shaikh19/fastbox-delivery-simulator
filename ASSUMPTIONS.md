# Engineering Assumptions & Design Decisions

This document outlines the engineering decisions, input format handling, and algorithm interpretations adopted for the FastBox Delivery Simulator.

---

## 1. Input Schema Normalization

The assignment ships two conflicting JSON schemas:

| Field | Schema A (`base_case.json`) | Schema B (`data.json`, `test_case_*.json`) |
| :--- | :--- | :--- |
| **warehouses** | `[{"id": "W1", "location": [0, 0]}]` | `{"W1": [0, 0]}` |
| **agents** | `[{"id": "A1", "location": [5, 5]}]` | `{"A1": [5, 5]}` |
| **packages** | `{"warehouse_id": "W1", ...}` | `{"warehouse": "W1", ...}` |

**Resolution:**
The parser auto-detects whether collections are lists or dictionaries, validates all coordinates and IDs, and normalizes them into a unified internal representation:
- `warehouses`: `dict[str, tuple[float, float]]`
- `agents`: `dict[str, tuple[float, float]]`
- `packages`: `list[dict[str, Any]]` with uniform key `"warehouse"`

---

## 2. Delivery & Routing Model

- **Sequential Chained Delivery:**
  An agent starts at their initial position. For each assigned package:
  $$\text{current position} \rightarrow \text{warehouse} \rightarrow \text{destination}$$
  After completing a delivery, the agent remains at that package's destination, which becomes the starting point for the subsequent package.
- **Input Order:**
  Packages assigned to an agent are serviced in their input sequence. No Travelling Salesperson (TSP) reordering is applied, adhering strictly to the problem statement.
- **Efficiency Metric:**
  $$\text{efficiency} = \frac{\text{total\_distance}}{\text{packages\_delivered}}$$
  For agents with 0 packages delivered, efficiency is defined as `0.0`.

---

## 3. PDF Illustrative Numbers vs. Written Algorithm

The sample report in the assignment PDF shows:
- `A1`: `total_distance = 85.32`, `efficiency = 42.66`
- `A2`: `total_distance = 120.12`, `efficiency = 60.06`
- `A3`: `total_distance = 50.00`, `efficiency = 50.00`
- `best_agent = "A1"`

### Verification:
Using the PDF's own coordinates (`W1: [0, 0]`, `W2: [50, 75]`, `W3: [100, 25]`, `A1: [5, 5]`, `A2: [60, 60]`, `A3: [95, 30]`), we tested both chained and independent delivery models:

1. **Chained sequential delivery (written rule):**
   - `A1` (P1, P4): $(5,5)\to W1 \to (30,40) \to W1 \to (10,10) = 7.07 + 50.00 + 50.00 + 14.14 = \mathbf{121.21}$ (eff: $60.61$)
   - `A2` (P2, P5): $(60,60)\to W2 \to (70,90) \to W2 \to (40,80) = 18.03 + 25.00 + 25.00 + 11.18 = \mathbf{79.21}$ (eff: $39.60$)
   - `A3` (P3): $(95,30)\to W3 \to (105,20) = 7.07 + 7.07 = \mathbf{14.14}$ (eff: $14.14$)
2. **Independent return-to-base trips:**
   - `A1`: $57.07 + 21.21 = \mathbf{78.28}$
   - `A2`: $43.03 + 29.21 = \mathbf{72.24}$
   - `A3`: $\mathbf{14.14}$

**Decision:**
Neither model matches the PDF's sample numbers. As per project guidelines, the written algorithm rules (Euclidean distance, nearest-agent assignment, sequential chained delivery) are implemented faithfully rather than forcing artificial numbers. Under true Euclidean calculation, Agent `A3` achieves the best efficiency ($14.14$).

---

## 4. Deterministic Tie-Breaking Rules

- **Equidistant Agents to a Warehouse:**
  When multiple agents share the exact same minimum distance to a warehouse, the agent whose ID sorts first lexicographically (e.g., `"A1"` before `"A2"`) is chosen.
- **Best Agent Selection:**
  1. Only agents that delivered at least one package (`packages_delivered > 0`) are considered.
  2. The agent with the lowest efficiency value is selected.
  3. If tied in efficiency, the agent with the higher number of packages delivered is selected.
  4. If still tied, the lexicographical order of the agent ID breaks the tie.

---

## 5. Input Validation

- Coordinates must be 2-element sequences of finite numbers (floats or ints). Booleans are explicitly rejected since `bool` subclasses `int` in Python.
- All IDs must be non-empty strings and unique within their collections.
- Every package's referenced warehouse must exist in the input `warehouses` collection.
