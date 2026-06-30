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
