import networkx as nx


def largest_component_fraction(graph: nx.Graph) -> float:
    """Fraction of current nodes that lie in the largest connected component."""
    n = graph.number_of_nodes()
    if n == 0:
        return 0.0
    largest = max(nx.connected_components(graph), key=len)
    return len(largest) / n


def global_efficiency(graph: nx.Graph) -> float:
    """Average inverse shortest-path distance over all node pairs (0..1).

    Robust to disconnection: unreachable pairs contribute 0.
    """
    if graph.number_of_nodes() < 2:
        return 0.0
    return nx.global_efficiency(graph)


def avg_shortest_path_in_largest_component(graph: nx.Graph) -> float:
    """Average shortest-path length, computed within the largest component only.

    Defined this way because average path length is undefined on a disconnected
    graph. Returns 0.0 if the largest component has fewer than 2 nodes.
    """
    if graph.number_of_nodes() == 0:
        return 0.0
    largest_nodes = max(nx.connected_components(graph), key=len)
    if len(largest_nodes) < 2:
        return 0.0
    sub = graph.subgraph(largest_nodes)
    return nx.average_shortest_path_length(sub)
