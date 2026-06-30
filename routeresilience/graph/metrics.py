import networkx as nx


def largest_component_fraction(graph: nx.Graph) -> float:
    """Fraction of current nodes that lie in the largest connected component."""
    n = graph.number_of_nodes()
    if n == 0:
        return 0.0
    largest = max(nx.connected_components(graph), key=len)
    return len(largest) / n
