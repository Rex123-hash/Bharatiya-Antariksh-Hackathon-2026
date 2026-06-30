# Route Resilience graph engine

The graph engine is the part of the system that is already built. It is plain Python on
top of NetworkX, with no dependency on imagery, models or a GPU, so it can be developed
and tested on its own.

Everything works on a NetworkX undirected graph whose nodes carry `x` and `y`
coordinates and whose edges carry a `length` weight. Once the road-extraction side of
the project is built, it only has to produce a graph in that shape; the engine itself
does not change.

## Modules

`routeresilience/graph/metrics.py`
Connectivity measures: the fraction of nodes in the largest connected component, global
efficiency, and the average shortest-path length within the largest component. These are
the numbers the collapse and scenario code reports.

`routeresilience/graph/criticality.py`
Ranks junctions by betweenness centrality (the "Gatekeeper Nodes"), and finds the
structural single points of failure, namely bridge edges and articulation nodes.

`routeresilience/graph/collapse.py`
Simulates a targeted attack. It repeatedly recomputes betweenness on the current graph,
removes the highest-scoring node, and records how connectivity decays. Recomputing at
each step models a cascading failure rather than a single fixed ranking.

`routeresilience/graph/scenarios.py`
Applies a disaster zone. Every edge with an endpoint inside a bounding box is disabled,
and the resulting connectivity loss is reported: edges removed, number of disconnected
sub-networks, and the size of the largest remaining component.

## Testing

The engine is covered by a pytest suite (33 tests). The tests use small graphs whose
expected values can be checked by hand. For example, a three-node path where the middle
node has a betweenness of 1.0, or two triangles joined at a single node so that removing
that node provably splits the graph in half.

`examples/demo.py` runs the whole engine on a small synthetic city (two neighbourhoods
joined by one river crossing) and prints the criticality ranking, a collapse curve and a
flood scenario.

```bash
python -m pip install networkx pytest
python examples/demo.py
python -m pytest -q
```

## Planned additions

The challenge expects several centrality measures compared against each other.
Betweenness is implemented. Current-flow betweenness, alpha-centrality and k-core are
short NetworkX calls and are the next thing to add, together with the Jaccard overlap of
each measure's top-ranked segments.
