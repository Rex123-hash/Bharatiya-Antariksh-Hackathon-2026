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
