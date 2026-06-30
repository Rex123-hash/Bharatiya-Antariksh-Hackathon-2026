# 🛰️ Route Resilience

### Occlusion-Robust Road Extraction & Graph-Theoretic Criticality Analysis for Urban Mobility

**Bharatiya Antariksh Hackathon 2026 · ISRO × Hack2skill · Challenge 4**

> Satellite road maps break where it matters most — under tree canopy, building
> shadows, and cloud cover. A broken map is useless for disaster response or traffic
> planning. **Route Resilience** rebuilds the *connected* road network from occluded
> satellite imagery, then turns it into a mathematical graph that answers the
> question city planners actually care about: **which roads, if they fail, break the
> city — and what happens when they do?**

---

## The problem

Modern Indian metros like Bengaluru face a dual failure in spatial modelling:

- **Fragmentation** — standard satellite road extraction suffers "spectral blindness."
  Canopy, shadow, and cloud chop the road mask into disconnected fragments.
- **Stagnation** — even a perfect mask is just pixels. It can't tell you where the
  network is fragile, or simulate what a flood or a collapsed flyover does to mobility.

Route Resilience bridges both gaps in one pipeline.

## Our approach

| Stage | What it does |
|------|--------------|
| **① Occlusion-robust segmentation** | A connectivity-aware model recovers a *topologically connected* road mask through canopy/shadow occlusion — built to feed the graph, not to chase pixel benchmarks. |
| **② Vectorization** | Skeletonize the mask into a weighted graph: nodes = junctions, edges = road segments (weighted by length, with optional travel-time estimates from road type). |
| **③ Graph resilience engine ★** | Rank critical bottlenecks, simulate progressive collapse, and model disaster scenarios — the differentiator and the heart of the demo. |
| **④ Interactive map app** | Pick an area → see roads → flip to graph → click to collapse the network → read live resilience metrics. |

**Why the graph engine is the star:** anyone can segment roads. Almost no one turns
that into a rigorous, interactive *resilience* tool. That's where this project wins.

## Architecture

```
 Satellite imagery (canopy · shadow · cloud)
                │
                ▼
 ①  Occlusion-robust segmentation  ──►  connected road mask
                │
                ▼
 ②  Vectorize  ──►  weighted graph (junctions + segments)
                │
                ▼
 ③  GRAPH RESILIENCE ENGINE  ★
        ├─ Criticality      betweenness · bridges · articulation points
        ├─ Collapse sim     progressive removal → connectivity-decay curves
        └─ Disaster zones   flood / blocked corridor → isolation impact
                │
                ▼
 ④  Interactive map web app
```

## What's built today

The **graph resilience engine (Stage ③) is implemented and fully test-driven** — pure
Python, no GPU, no downloads:

| Capability | Module |
|------------|--------|
| Connectivity metrics (largest component, global efficiency, avg shortest path) | `routeresilience/graph/metrics.py` |
| Criticality (betweenness ranking, bridge roads, articulation junctions) | `routeresilience/graph/criticality.py` |
| Collapse simulation (smart-adversary node removal → decay curve) | `routeresilience/graph/collapse.py` |
| Disaster scenarios (zone knockout → connectivity-loss metrics) | `routeresilience/graph/scenarios.py` |

✅ **Comprehensive test suite passing.** The other stages plug in by simply handing the
engine a `networkx.Graph` with `x`/`y` node coordinates and `length` edge weights — the
engine never changes.

## Quickstart

```bash
# 1. Install dependencies
python -m pip install networkx pytest

# 2. Run the demo (analyzes a synthetic city with a single river crossing)
python examples/demo.py

# 3. Run the test suite
python -m pytest -q
```

### Example output

```
== Most critical junctions (betweenness) ==
   BL  score=0.556        <- the river-crossing bridge dominates every cross-city trip
   BR  score=0.556

== Structural weak points ==
  Bridge roads (single points of failure): [('BL', 'BR')]
  Articulation junctions:                  ['BR', 'BL']

== Targeted collapse (remove the 2 most critical junctions) ==
  removed 0 [(start)] -> largest-component 100%, efficiency 0.544
  removed 1 [    BL] -> largest-component  56%, efficiency 0.361   <- one node, city halves

== Flood scenario: river corridor is impassable ==
  road segments cut:         5
  disconnected sub-networks:  3
  largest reachable area:    40% of the city
```

## Roadmap

- [x] **Graph resilience engine** — criticality, collapse simulation, disaster scenarios
- [ ] Real OSM ingestion → run on actual Bengaluru roads
- [ ] Occlusion-robust segmentation model (connectivity-aware loss) + synthetic-occlusion robustness benchmark
- [ ] Mask → graph vectorization
- [ ] Population / hospital impact overlay (people isolated, facilities cut off)
- [ ] Interactive map web app
- [ ] *Future scope:* resilience optimization — where to add a road for max resilience per rupee

## Tech stack

**Core engine:** Python 3.11+ · NetworkX · pytest
**Planned:** PyTorch (segmentation) · OSMnx / Rasterio (geospatial) · Leaflet / Streamlit (app)

## Repository structure

```
routeresilience/graph/   core graph resilience engine
examples/demo.py         runnable end-to-end demo
tests/                   test suite
docs/design/             design spec & implementation plan
```

## Team

**Web Hackers** — Bharatiya Antariksh Hackathon 2026

## Acknowledgements

Built for the **Bharatiya Antariksh Hackathon 2026**, a national innovation initiative
by the **Indian Space Research Organisation (ISRO)**, powered by **Hack2skill**.
