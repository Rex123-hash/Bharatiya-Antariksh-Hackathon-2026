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
