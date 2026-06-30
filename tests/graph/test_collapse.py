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
