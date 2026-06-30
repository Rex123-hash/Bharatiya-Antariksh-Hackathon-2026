# Route Resilience — Graph Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Module 2 graph resilience engine — criticality ranking, collapse simulation, and disaster-scenario metrics — as a pure-Python, fully tested library, independent of any imagery or model.

**Architecture:** Plain `networkx` undirected graphs are the universal input. Pure functions compute metrics, rank critical elements, simulate progressive removal, and apply disaster zones. Real OSM/road-mask ingestion plugs in later by simply producing a `networkx.Graph` with `length` edge weights — the engine never depends on it.

**Tech Stack:** Python 3.11+, networkx 3.x, pytest. (No GPU, no geodata downloads required for this plan.)

---

### Task 1: Project scaffold + connectivity metric

**Files:**
- Create: `pyproject.toml`
- Create: `routeresilience/__init__.py`
- Create: `routeresilience/graph/__init__.py`
- Create: `routeresilience/graph/metrics.py`
- Create: `tests/__init__.py`
- Create: `tests/graph/__init__.py`
- Test: `tests/graph/test_metrics.py`

- [ ] **Step 1: Create the package scaffold and pyproject**

`pyproject.toml`:
```toml
[project]
name = "routeresilience"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["networkx>=3.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

Create empty files: `routeresilience/__init__.py`, `routeresilience/graph/__init__.py`, `tests/__init__.py`, `tests/graph/__init__.py`.

- [ ] **Step 2: Initialize git and install deps**

The `pythonpath = ["."]` pytest setting makes `routeresilience` importable from the
repo root, so no editable install is needed (avoids setuptools auto-discovery errors
from the flat `routeresilience/` + `tests/` layout).

```bash
git init
python -m pip install "networkx>=3.0" "pytest>=8.0"
```

- [ ] **Step 3: Write the failing test**

`tests/graph/test_metrics.py`:
```python
import networkx as nx
from routeresilience.graph.metrics import largest_component_fraction


def test_fully_connected_path_is_fraction_one():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    assert largest_component_fraction(g) == 1.0


def test_removing_articulation_node_splits_graph():
    g = nx.Graph()
    g.add_nodes_from(["A", "C"])  # B already removed; A and C isolated
    assert largest_component_fraction(g) == 0.5


def test_empty_graph_is_zero():
    assert largest_component_fraction(nx.Graph()) == 0.0
```

- [ ] **Step 4: Run test to verify it fails**

Run: `python -m pytest tests/graph/test_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError`/`ImportError` for `largest_component_fraction`.

- [ ] **Step 5: Write minimal implementation**

`routeresilience/graph/metrics.py`:
```python
import networkx as nx


def largest_component_fraction(graph: nx.Graph) -> float:
    """Fraction of current nodes that lie in the largest connected component."""
    n = graph.number_of_nodes()
    if n == 0:
        return 0.0
    largest = max(nx.connected_components(graph), key=len)
    return len(largest) / n
```

- [ ] **Step 6: Run test to verify it passes**

Run: `python -m pytest tests/graph/test_metrics.py -v`
Expected: PASS (3 passed).

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml routeresilience tests
git commit -m "feat: scaffold package and largest-component-fraction metric"
```

---

### Task 2: Efficiency + average-shortest-path metrics

**Files:**
- Modify: `routeresilience/graph/metrics.py`
- Test: `tests/graph/test_metrics.py`

- [ ] **Step 1: Write the failing test (append to file)**

Append to `tests/graph/test_metrics.py`:
```python
from routeresilience.graph.metrics import (
    global_efficiency,
    avg_shortest_path_in_largest_component,
)


def test_global_efficiency_triangle_is_one():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("A", "C")])
    # every pair is distance 1 -> efficiency 1.0
    assert global_efficiency(g) == 1.0


def test_global_efficiency_disconnected_drops_below_one():
    g = nx.Graph()
    g.add_edges_from([("A", "B")])
    g.add_nodes_from(["C"])  # C isolated
    assert global_efficiency(g) < 1.0


def test_avg_shortest_path_path_graph():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    # distances: A-B=1, B-C=1, A-C=2 ; mean = 4/3
    assert round(avg_shortest_path_in_largest_component(g), 4) == round(4 / 3, 4)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/graph/test_metrics.py -v`
Expected: FAIL (ImportError for the two new names).

- [ ] **Step 3: Write minimal implementation (append to metrics.py)**

Append to `routeresilience/graph/metrics.py`:
```python
def global_efficiency(graph: nx.Graph) -> float:
    """Average inverse shortest-path distance over all node pairs (0..1).

    Robust to disconnection: unreachable pairs contribute 0.
    """
    if graph.number_of_nodes() < 2:
        return 0.0
    return nx.global_efficiency(graph)


def avg_shortest_path_in_largest_component(graph: nx.Graph) -> float:
    """Average shortest-path length, computed within the largest component only.

    Defined this way because average path length is undefined on a disconnected
    graph. Returns 0.0 if the largest component has fewer than 2 nodes.
    """
    if graph.number_of_nodes() == 0:
        return 0.0
    largest_nodes = max(nx.connected_components(graph), key=len)
    if len(largest_nodes) < 2:
        return 0.0
    sub = graph.subgraph(largest_nodes)
    return nx.average_shortest_path_length(sub)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/graph/test_metrics.py -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add routeresilience/graph/metrics.py tests/graph/test_metrics.py
git commit -m "feat: add global-efficiency and avg-shortest-path metrics"
```

---

### Task 3: Criticality — betweenness ranking

**Files:**
- Create: `routeresilience/graph/criticality.py`
- Test: `tests/graph/test_criticality.py`

- [ ] **Step 1: Write the failing test**

`tests/graph/test_criticality.py`:
```python
import networkx as nx
from routeresilience.graph.criticality import rank_nodes_by_betweenness


def test_middle_node_of_path_is_most_critical():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    ranking = rank_nodes_by_betweenness(g)
    # returns list of (node, score) sorted descending
    assert ranking[0][0] == "B"
    assert ranking[0][1] == 1.0
    assert {n for n, _ in ranking} == {"A", "B", "C"}


def test_ranking_is_sorted_descending():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("C", "D")])
    scores = [s for _, s in rank_nodes_by_betweenness(g)]
    assert scores == sorted(scores, reverse=True)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/graph/test_criticality.py -v`
Expected: FAIL (ImportError).

- [ ] **Step 3: Write minimal implementation**

`routeresilience/graph/criticality.py`:
```python
import networkx as nx


def rank_nodes_by_betweenness(graph: nx.Graph, weight: str | None = None):
    """Rank nodes by betweenness centrality, highest first.

    Args:
        graph: undirected road graph.
        weight: optional edge attribute to use as distance (e.g. "length").
                None = treat every edge as unit length.

    Returns:
        list of (node, score) tuples sorted by score descending.
    """
    scores = nx.betweenness_centrality(graph, weight=weight)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/graph/test_criticality.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add routeresilience/graph/criticality.py tests/graph/test_criticality.py
git commit -m "feat: rank nodes by betweenness centrality"
```

---

### Task 4: Criticality — bridges & articulation points

**Files:**
- Modify: `routeresilience/graph/criticality.py`
- Test: `tests/graph/test_criticality.py`

- [ ] **Step 1: Write the failing test (append)**

Append to `tests/graph/test_criticality.py`:
```python
from routeresilience.graph.criticality import (
    find_bridge_edges,
    find_articulation_nodes,
)


def test_path_graph_all_edges_are_bridges():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    bridges = find_bridge_edges(g)
    assert {frozenset(e) for e in bridges} == {
        frozenset(("A", "B")),
        frozenset(("B", "C")),
    }


def test_triangle_has_no_bridges():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("A", "C")])
    assert find_bridge_edges(g) == []


def test_path_graph_middle_is_articulation_point():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    assert find_articulation_nodes(g) == ["B"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/graph/test_criticality.py -v`
Expected: FAIL (ImportError for new names).

- [ ] **Step 3: Write minimal implementation (append)**

Append to `routeresilience/graph/criticality.py`:
```python
def find_bridge_edges(graph: nx.Graph):
    """Edges whose removal increases the number of connected components."""
    return list(nx.bridges(graph))


def find_articulation_nodes(graph: nx.Graph):
    """Nodes whose removal increases the number of connected components."""
    return list(nx.articulation_points(graph))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/graph/test_criticality.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add routeresilience/graph/criticality.py tests/graph/test_criticality.py
git commit -m "feat: detect bridge edges and articulation nodes"
```

---

### Task 5: Collapse simulation — progressive removal curve

**Files:**
- Create: `routeresilience/graph/collapse.py`
- Test: `tests/graph/test_collapse.py`

- [ ] **Step 1: Write the failing test**

`tests/graph/test_collapse.py`:
```python
import networkx as nx
from routeresilience.graph.collapse import simulate_targeted_collapse


def test_collapse_curve_starts_at_full_connectivity():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("C", "D")])
    result = simulate_targeted_collapse(g, steps=2)
    # step 0 = no removal -> fraction 1.0
    assert result[0]["removed"] == 0
    assert result[0]["largest_component_fraction"] == 1.0


def test_collapse_removes_most_critical_first_and_fragments():
    # Two triangles joined by a single bridge node B:
    #   A-C-A' triangle on left, D-E-D' on right, all hinging through B
    g = nx.Graph()
    g.add_edges_from(
        [("A", "C"), ("C", "B"), ("B", "A")]  # left triangle through B
        + [("B", "D"), ("D", "E"), ("E", "B")]  # right triangle through B
    )
    result = simulate_targeted_collapse(g, steps=1)
    # removing the highest-betweenness node (B) should reduce connectivity
    assert result[1]["removed"] == 1
    assert result[1]["largest_component_fraction"] < 1.0


def test_steps_capped_at_node_count():
    g = nx.Graph()
    g.add_edges_from([("A", "B")])
    result = simulate_targeted_collapse(g, steps=10)
    # cannot remove more nodes than exist
    assert len(result) <= g.number_of_nodes() + 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/graph/test_collapse.py -v`
Expected: FAIL (ImportError).

- [ ] **Step 3: Write minimal implementation**

`routeresilience/graph/collapse.py`:
```python
import networkx as nx

from routeresilience.graph.criticality import rank_nodes_by_betweenness
from routeresilience.graph.metrics import (
    largest_component_fraction,
    global_efficiency,
)


def simulate_targeted_collapse(graph: nx.Graph, steps: int, weight: str | None = None):
    """Remove the most-critical node repeatedly, recording connectivity decay.

    At each step: recompute betweenness on the *current* graph, remove the single
    highest-scoring node, and record connectivity metrics. Recomputing each step
    models a smart adversary / cascading failure rather than a one-shot ranking.

    Returns a list of dicts (one per step incl. step 0 = untouched):
        {"removed": int, "node": node|None,
         "largest_component_fraction": float, "global_efficiency": float}
    """
    working = graph.copy()
    curve = [
        {
            "removed": 0,
            "node": None,
            "largest_component_fraction": largest_component_fraction(working),
            "global_efficiency": global_efficiency(working),
        }
    ]
    removable = min(steps, working.number_of_nodes())
    for i in range(1, removable + 1):
        ranking = rank_nodes_by_betweenness(working, weight=weight)
        if not ranking:
            break
        victim = ranking[0][0]
        working.remove_node(victim)
        curve.append(
            {
                "removed": i,
                "node": victim,
                "largest_component_fraction": largest_component_fraction(working),
                "global_efficiency": global_efficiency(working),
            }
        )
    return curve
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/graph/test_collapse.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add routeresilience/graph/collapse.py tests/graph/test_collapse.py
git commit -m "feat: targeted collapse simulation with connectivity-decay curve"
```

---

### Task 6: Disaster scenario — remove a zone, report impact

**Files:**
- Create: `routeresilience/graph/scenarios.py`
- Test: `tests/graph/test_scenarios.py`

- [ ] **Step 1: Write the failing test**

`tests/graph/test_scenarios.py`:
```python
import networkx as nx
from routeresilience.graph.scenarios import apply_disaster_zone


def _grid():
    # 2x2 grid of nodes at integer coords, 4 edges forming a square
    g = nx.Graph()
    coords = {"A": (0, 0), "B": (1, 0), "C": (1, 1), "D": (0, 1)}
    for node, xy in coords.items():
        g.add_node(node, x=xy[0], y=xy[1])
    g.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")])
    return g


def test_zone_disables_edges_inside_bbox():
    g = _grid()
    # bbox covering only node B's corner removes edges touching B
    result = apply_disaster_zone(g, bbox=(0.9, -0.1, 1.1, 0.1))
    assert result["edges_removed"] == 2  # A-B and B-C touch B
    assert result["disconnected_segments"] >= 0


def test_no_overlap_zone_changes_nothing():
    g = _grid()
    result = apply_disaster_zone(g, bbox=(5, 5, 6, 6))
    assert result["edges_removed"] == 0
    assert result["largest_component_fraction_after"] == 1.0


def test_zone_reports_connectivity_drop():
    g = _grid()
    result = apply_disaster_zone(g, bbox=(0.9, -0.1, 1.1, 1.1))  # covers B and C
    # removing B and C's edges isolates them from A-D
    assert result["largest_component_fraction_after"] < 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/graph/test_scenarios.py -v`
Expected: FAIL (ImportError).

- [ ] **Step 3: Write minimal implementation**

`routeresilience/graph/scenarios.py`:
```python
import networkx as nx

from routeresilience.graph.metrics import largest_component_fraction


def _node_in_bbox(graph: nx.Graph, node, bbox) -> bool:
    min_x, min_y, max_x, max_y = bbox
    x = graph.nodes[node]["x"]
    y = graph.nodes[node]["y"]
    return min_x <= x <= max_x and min_y <= y <= max_y


def apply_disaster_zone(graph: nx.Graph, bbox):
    """Disable every edge with at least one endpoint inside an axis-aligned bbox.

    bbox = (min_x, min_y, max_x, max_y). Nodes must carry "x"/"y" attributes.

    Returns floor metrics (graph-only, no external data required):
        {"edges_removed": int,
         "disconnected_segments": int,   # components beyond the first
         "largest_component_fraction_after": float}
    """
    working = graph.copy()
    inside = {n for n in working.nodes if _node_in_bbox(working, n, bbox)}
    to_remove = [
        (u, v) for u, v in working.edges if u in inside or v in inside
    ]
    working.remove_edges_from(to_remove)
    num_components = nx.number_connected_components(working)
    return {
        "edges_removed": len(to_remove),
        "disconnected_segments": max(0, num_components - 1),
        "largest_component_fraction_after": largest_component_fraction(working),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/graph/test_scenarios.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add routeresilience/graph/scenarios.py tests/graph/test_scenarios.py
git commit -m "feat: disaster-zone scenario with graph-only impact metrics"
```

---

### Task 7: Full-engine smoke test + run-all

**Files:**
- Test: `tests/graph/test_engine_integration.py`

- [ ] **Step 1: Write the integration test**

`tests/graph/test_engine_integration.py`:
```python
import networkx as nx
from routeresilience.graph.criticality import (
    rank_nodes_by_betweenness,
    find_bridge_edges,
    find_articulation_nodes,
)
from routeresilience.graph.collapse import simulate_targeted_collapse
from routeresilience.graph.scenarios import apply_disaster_zone


def _city():
    g = nx.Graph()
    coords = {
        "A": (0, 0), "B": (1, 0), "C": (2, 0),
        "D": (0, 1), "E": (1, 1), "F": (2, 1),
    }
    for n, (x, y) in coords.items():
        g.add_node(n, x=x, y=y)
    g.add_edges_from(
        [("A", "B"), ("B", "C"), ("D", "E"), ("E", "F"),
         ("A", "D"), ("B", "E"), ("C", "F")]
    )
    for u, v in g.edges:
        g[u][v]["length"] = 1.0
    return g


def test_engine_end_to_end_runs_and_is_consistent():
    g = _city()

    ranking = rank_nodes_by_betweenness(g, weight="length")
    assert len(ranking) == g.number_of_nodes()

    # connected grid -> no bridges, no articulation points
    assert find_bridge_edges(g) == []
    assert find_articulation_nodes(g) == []

    curve = simulate_targeted_collapse(g, steps=3, weight="length")
    # connectivity is non-increasing as we remove critical nodes
    fractions = [pt["largest_component_fraction"] for pt in curve]
    assert fractions[0] == 1.0
    assert fractions[-1] <= fractions[0]

    impact = apply_disaster_zone(g, bbox=(0.9, -0.1, 1.1, 1.1))  # column B-E
    assert impact["edges_removed"] > 0
```

- [ ] **Step 2: Run the full suite**

Run: `python -m pytest -v`
Expected: PASS (all tests across every module green).

- [ ] **Step 3: Commit**

```bash
git add tests/graph/test_engine_integration.py
git commit -m "test: end-to-end graph-engine integration smoke test"
```

---

## Out of scope for this plan (separate plans later)

- Data pipeline (Bengaluru optical imagery + OSM ingestion → `networkx.Graph`).
- Module 1 segmentation model (clDice + Dice/BCE) and synthetic-occlusion harness.
- Mask → graph vectorization (skeletonize → nodes/edges with `length`).
- Population/hospital impact overlay (WorldPop/GHS-POP + OSM `amenity=hospital`).
- Interactive map web app.

The engine here is built so each of those plugs in by producing a `networkx.Graph`
with `x`/`y` node coords and `length` edge weights — nothing in this plan changes.
