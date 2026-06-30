import networkx as nx

from routeresilience.graph.criticality import rank_nodes_by_betweenness
from routeresilience.graph.metrics import (
    largest_component_fraction,
    global_efficiency,
)


def simulate_targeted_collapse(graph: nx.Graph, steps: int, weight: str | None = None):
    """Remove the most-critical node repeatedly, recording connectivity decay.

    At each step: recompute betweenness on the *current* graph, remove the single
    highest-scoring node, and record connectivity metrics. Recomputing each step
    models a smart adversary / cascading failure rather than a one-shot ranking.

    Returns a list of dicts (one per step incl. step 0 = untouched):
        {"removed": int, "node": node|None,
         "largest_component_fraction": float, "global_efficiency": float}
    """
    working = graph.copy()
    curve = [
        {
            "removed": 0,
            "node": None,
            "largest_component_fraction": largest_component_fraction(working),
            "global_efficiency": global_efficiency(working),
        }
    ]
    removable = min(steps, working.number_of_nodes())
    for i in range(1, removable + 1):
        ranking = rank_nodes_by_betweenness(working, weight=weight)
        if not ranking:
            break
        victim = ranking[0][0]
        working.remove_node(victim)
        curve.append(
            {
                "removed": i,
                "node": victim,
                "largest_component_fraction": largest_component_fraction(working),
                "global_efficiency": global_efficiency(working),
            }
        )
    return curve
