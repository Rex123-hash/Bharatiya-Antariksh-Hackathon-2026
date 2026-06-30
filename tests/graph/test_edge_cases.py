"""Additional edge-case and robustness tests across the graph engine."""

import networkx as nx

from routeresilience.graph.metrics import (
    largest_component_fraction,
    global_efficiency,
    avg_shortest_path_in_largest_component,
)
from routeresilience.graph.criticality import (
    rank_nodes_by_betweenness,
    find_bridge_edges,
    find_articulation_nodes,
)
from routeresilience.graph.collapse import simulate_targeted_collapse
from routeresilience.graph.scenarios import apply_disaster_zone


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #

def test_largest_component_fraction_with_multiple_components():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])  # component of 3
    g.add_edges_from([("D", "E")])  # component of 2
    # largest = 3 of 5 nodes
    assert largest_component_fraction(g) == 0.6


def test_global_efficiency_single_node_is_zero():
    g = nx.Graph()
    g.add_node("A")
    assert global_efficiency(g) == 0.0


def test_avg_shortest_path_single_node_is_zero():
    g = nx.Graph()
    g.add_node("A")
    assert avg_shortest_path_in_largest_component(g) == 0.0


def test_avg_shortest_path_ignores_isolated_nodes():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    g.add_node("D")  # isolated; must not break the calculation
    # computed within the largest component {A,B,C}: mean of (1,1,2) = 4/3
    assert round(avg_shortest_path_in_largest_component(g), 4) == round(4 / 3, 4)


# --------------------------------------------------------------------------- #
# criticality
# --------------------------------------------------------------------------- #

def test_betweenness_on_empty_graph_is_empty_list():
    assert rank_nodes_by_betweenness(nx.Graph()) == []


def test_betweenness_scores_are_in_unit_range():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A", "C")])
    for _, score in rank_nodes_by_betweenness(g):
        assert 0.0 <= score <= 1.0


def test_weighted_betweenness_returns_all_nodes():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    for u, v in g.edges:
        g[u][v]["length"] = 1.0
    ranking = rank_nodes_by_betweenness(g, weight="length")
    assert {n for n, _ in ranking} == {"A", "B", "C"}


def test_bridge_in_cycle_with_tail():
    # triangle A-B-C with a tail C-D ; only C-D is a bridge, C is articulation
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("A", "C"), ("C", "D")])
    assert {frozenset(e) for e in find_bridge_edges(g)} == {frozenset(("C", "D"))}
    assert find_articulation_nodes(g) == ["C"]


def test_criticality_on_empty_graph():
    assert find_bridge_edges(nx.Graph()) == []
    assert find_articulation_nodes(nx.Graph()) == []


# --------------------------------------------------------------------------- #
# collapse
# --------------------------------------------------------------------------- #

def test_collapse_with_zero_steps_returns_only_start():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    curve = simulate_targeted_collapse(g, steps=0)
    assert len(curve) == 1
    assert curve[0]["removed"] == 0
    assert curve[0]["node"] is None


def test_collapse_never_improves_connectivity_overall():
    # two triangles joined only through B -> a strong bottleneck
    g = nx.Graph()
    g.add_edges_from(
        [("A", "C"), ("C", "B"), ("B", "A"), ("B", "D"), ("D", "E"), ("E", "B")]
    )
    curve = simulate_targeted_collapse(g, steps=2)
    assert curve[-1]["largest_component_fraction"] <= curve[0]["largest_component_fraction"]
    assert curve[-1]["global_efficiency"] <= curve[0]["global_efficiency"]


def test_collapse_length_never_exceeds_node_count_plus_one():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C")])
    curve = simulate_targeted_collapse(g, steps=99)
    assert 1 <= len(curve) <= g.number_of_nodes() + 1


# --------------------------------------------------------------------------- #
# scenarios
# --------------------------------------------------------------------------- #

def _square_grid():
    g = nx.Graph()
    coords = {"A": (0, 0), "B": (1, 0), "C": (1, 1), "D": (0, 1)}
    for node, (x, y) in coords.items():
        g.add_node(node, x=x, y=y)
    g.add_edges_from([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")])
    return g


def test_disaster_zone_boundary_is_inclusive():
    g = _square_grid()
    # a degenerate bbox sitting exactly on node B's coordinate still catches B
    result = apply_disaster_zone(g, bbox=(1, 0, 1, 0))
    assert result["edges_removed"] == 2  # A-B and B-C touch B


def test_disaster_zone_with_no_overlap_reports_zero_segments():
    g = _square_grid()
    result = apply_disaster_zone(g, bbox=(9, 9, 10, 10))
    assert result["edges_removed"] == 0
    assert result["disconnected_segments"] == 0
    assert result["largest_component_fraction_after"] == 1.0


def test_disaster_zone_counts_all_edges_touching_a_corner():
    g = _square_grid()
    # bbox over corner A only -> edges A-B and D-A
    result = apply_disaster_zone(g, bbox=(-0.1, -0.1, 0.1, 0.1))
    assert result["edges_removed"] == 2
