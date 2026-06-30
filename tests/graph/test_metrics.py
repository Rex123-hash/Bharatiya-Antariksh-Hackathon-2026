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
