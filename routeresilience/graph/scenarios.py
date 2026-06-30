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
