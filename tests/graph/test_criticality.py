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
