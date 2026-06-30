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


def find_bridge_edges(graph: nx.Graph):
    """Edges whose removal increases the number of connected components."""
    return list(nx.bridges(graph))


def find_articulation_nodes(graph: nx.Graph):
    """Nodes whose removal increases the number of connected components."""
    return list(nx.articulation_points(graph))
