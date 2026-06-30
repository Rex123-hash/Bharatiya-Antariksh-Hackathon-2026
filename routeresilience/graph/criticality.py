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
