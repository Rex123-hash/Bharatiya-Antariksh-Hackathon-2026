"""Runnable demo of the Route Resilience graph engine.

Builds a small synthetic city whose two halves hang off a single river-crossing
bridge, then shows criticality ranking, collapse simulation, and a flood scenario.

Run from the project root:
    python examples/demo.py
"""

import math
import sys
import pathlib

# Make the package importable when run as a plain script from anywhere.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import networkx as nx

from routeresilience.graph.criticality import (
    rank_nodes_by_betweenness,
    find_bridge_edges,
    find_articulation_nodes,
)
from routeresilience.graph.collapse import simulate_targeted_collapse
from routeresilience.graph.scenarios import apply_disaster_zone


def build_demo_city() -> nx.Graph:
    """Two 4-node blocks joined only by the BL--BR river crossing."""
    coords = {
        # west block
        "W1": (0, 0), "W2": (1, 0), "W3": (0, 1), "W4": (1, 1),
        # the single bridge across the river
        "BL": (2, 0.5), "BR": (3, 0.5),
        # east block
        "E1": (4, 0), "E2": (5, 0), "E3": (4, 1), "E4": (5, 1),
    }
    edges = [
        ("W1", "W2"), ("W1", "W3"), ("W2", "W4"), ("W3", "W4"), ("W2", "BL"), ("W4", "BL"),
        ("BL", "BR"),  # <-- the only river crossing
        ("BR", "E1"), ("BR", "E3"), ("E1", "E2"), ("E1", "E3"), ("E2", "E4"), ("E3", "E4"),
    ]
    g = nx.Graph()
    for node, (x, y) in coords.items():
        g.add_node(node, x=x, y=y)
    for u, v in edges:
        ux, uy = coords[u]
        vx, vy = coords[v]
        g.add_edge(u, v, length=math.dist((ux, uy), (vx, vy)))
    return g


def main() -> None:
    g = build_demo_city()
    print(f"City: {g.number_of_nodes()} junctions, {g.number_of_edges()} road segments\n")

    print("== Most critical junctions (betweenness) ==")
    for node, score in rank_nodes_by_betweenness(g, weight="length")[:4]:
        print(f"  {node:>3}  score={score:.3f}")

    print("\n== Structural weak points ==")
    print(f"  Bridge roads (single points of failure): {find_bridge_edges(g)}")
    print(f"  Articulation junctions:                  {find_articulation_nodes(g)}")

    print("\n== Targeted collapse (remove the 2 most critical junctions) ==")
    for pt in simulate_targeted_collapse(g, steps=2, weight="length"):
        node = pt["node"] or "(start)"
        print(
            f"  removed {pt['removed']} [{node:>6}] -> "
            f"largest-component {pt['largest_component_fraction']:.0%}, "
            f"efficiency {pt['global_efficiency']:.3f}"
        )

    print("\n== Flood scenario: river corridor (x in 1.5..3.5) is impassable ==")
    impact = apply_disaster_zone(g, bbox=(1.5, -1, 3.5, 2))
    print(f"  road segments cut:        {impact['edges_removed']}")
    print(f"  disconnected sub-networks: {impact['disconnected_segments']}")
    print(f"  largest reachable area:    {impact['largest_component_fraction_after']:.0%} of the city")


if __name__ == "__main__":
    main()
