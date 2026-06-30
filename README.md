<p align="center">
  <img src="assets/logo.svg" alt="Route Resilience logo" width="104" />
</p>

<h1 align="center">Route Resilience</h1>

<p align="center"><b>Occlusion-Robust Road Extraction &amp; Graph-Theoretic Criticality Analysis for Urban Mobility</b></p>

<p align="center">Bharatiya Antariksh Hackathon 2026 &nbsp;·&nbsp; ISRO &times; Hack2skill &nbsp;·&nbsp; Challenge 4</p>

---

> Satellite road maps break where it matters most — under tree canopy, building
> shadows, and cloud cover. A broken map is useless for disaster response or traffic
> planning. **Route Resilience** rebuilds the *connected* road network from occluded
> satellite imagery, then turns it into a mathematical graph that answers the question
> city planners actually care about: **which roads, if they fail, break the city — and
> what happens when they do?**

## Table of contents

- [The challenge](#the-challenge)
- [Our approach](#our-approach)
- [The pipeline](#the-pipeline)
- [Criticality analysis](#criticality-analysis)
- [Resilience under disruption](#resilience-under-disruption)
- [Evaluation metrics](#evaluation-metrics)
- [What's built today](#whats-built-today)
- [Quickstart](#quickstart)
- [Example output](#example-output)
- [Repository structure](#repository-structure)
- [Roadmap](#roadmap)
- [Technology stack](#technology-stack)
- [Team](#team)

## The challenge

Modern urban centres, particularly rapidly expanding Indian metropolises such as
Bengaluru, face a **dual challenge** in spatial modelling:

- **Fragmentation** — standard satellite-based road extraction often fails due to
  *spectral blindness* caused by tree canopies, building shadows, and cloud cover.
  These "broken" masks are useless for real-world applications like disaster response
  or traffic simulation because they lack topological connectivity.
- **Stagnation** — even a perfect road mask is just pixels. It cannot tell a planner
  which junctions are systemic bottlenecks, what happens to mobility if a key flyover
  fails, or how many people are cut off when a corridor floods.

Route Resilience bridges this gap with an end-to-end pipeline: first, using
context-aware deep learning to "see through" occlusions and recover a *connected* road
network; second, transforming those masks into a mathematically continuous, weighted
graph to identify systemic bottlenecks and simulate urban-collapse scenarios.

## Our approach

| Stage | What it does |
|------|--------------|
| **1. Multi-source urban data** | Primary imagery: Sentinel-2 (10 m), Resourcesat LISS-IV (5.8 m), Cartosat-3 (high-res). Ground truth & pre-training: OpenStreetMap, SpaceNet, DeepGlobe, OpenSatMap — zero manual annotation. |
| **2. Occlusion-aware extraction** | A **Transformer-based**, connectivity-aware deep-learning model recovers a *topologically connected* road mask through canopy, shadow, vehicles and clutter — optimised for occlusion-recall, not just pixel benchmarks. |
| **3. Topological reconstruction** | Extracted mask → **MST + Disjoint-Set (Union-Find) "healing"** → a routable weighted graph (nodes = junctions, edges = road segments weighted by length / travel-time). |
| **4. Criticality analysis** | Rank critical bottlenecks using multiple complementary centrality measures and structural detectors. |
| **5. Resilience under disruption** | Simulate progressive failure and disaster scenarios, measuring how the network fragments. |
| **6. Interactive map app** | Pick an area → see roads → flip to graph → click to collapse the network → read live resilience metrics. |

**Why the graph engine is the star:** anyone can segment roads. Almost no one turns
that into a rigorous, interactive *resilience* tool. That is where this project wins.

## The pipeline

```
 Imagery        Sentinel-2 · Resourcesat LISS-IV · Cartosat-3
 Ground truth   OpenStreetMap · SpaceNet · DeepGlobe · OpenSatMap
                │
                ▼
 Occlusion-aware extraction   (Transformer + connectivity-aware clDice loss)
                │
                ▼
 Topological reconstruction   (MST + Disjoint-Set "healing" → routable weighted graph)
                │
                ▼
 GRAPH RESILIENCE ENGINE  (the star)
        ├─ Structural intelligence   Gatekeeper Nodes (BC) · CFBC · α-centrality · k-core · bridges · articulation
        ├─ Collapse simulation       progressive removal → connectivity-decay curves
        └─ Disaster stress-test      flood / accident → isolation, rerouting & travel-time impact
                │
                ▼
 Interactive map app   (Resilience Index)
```

## Criticality analysis

A resilient-routing analysis is only as good as its definition of "critical." The
highest-importance junctions — the city's **"Gatekeeper Nodes"** — are single points of
failure whose loss fragments mobility. Different centrality measures capture
**complementary** aspects of how important a road segment is, so we rank critical
segments with several and compare them:

| Measure | What it captures |
|---------|------------------|
| **Betweenness Centrality (BC)** | Segments that lie on the most shortest paths — classic traffic bottlenecks. |
| **Current-Flow Betweenness (CFBC)** | Bottlenecks under a *flow* model, where traffic spreads across alternative routes rather than only the shortest path. |
| **α-Centrality** | Influence that accounts for both network structure and external/background importance. |
| **k-Core** | How deeply embedded a segment is in densely connected cores versus fragile peripheries. |
| **Bridges & articulation points** | Single points of failure whose removal *disconnects* the network outright. |

Agreement between measures is summarised as the **Jaccard overlap of the top-10% most
critical segments** — high overlap means a segment is critical no matter how you define
importance.

## Resilience under disruption

We quantify resilience the way infrastructure engineers do: by knocking elements out
and watching the network break. As critical junctions/segments are progressively
removed (a targeted "smart-adversary" attack, or a localized disaster zone), we track
**network connectivity = the size of the giant (largest) connected component**, along
with global efficiency and the number of disconnected sub-networks. The result is a
**connectivity-decay curve** and disaster-impact figures (population isolated,
facilities cut off) that turn abstract graph theory into planning decisions.

## Evaluation metrics

Aligned with the challenge's official evaluation parameters:

**Road extraction**
- **IoU & Dice — focus on Occlusion-Recall** — recovery of roads hidden under shadow and canopy.
- **Generalisation** — accuracy across dense-urban, forested-suburban, and rural terrains.
- **Length-Complete / Relaxed IoU** — a 3–5 px tolerance buffer so minor alignment shifts aren't penalised.

**Topology & resilience**
- **Connectivity Ratio** — percentage increase in the largest connected component after the MST healing phase. *(The engine computes this directly.)*
- **Topological Accuracy** — Average Path Length error vs OSM (shortest path between random point pairs, ground truth vs model graph). *(The engine computes this directly.)*
- **Resilience Index** — connectivity loss, rerouting, and travel-time increase as Gatekeeper Nodes fail.

## What's built today

The **graph resilience engine is implemented and fully test-driven** — pure Python, no
GPU, no downloads:

| Capability | Module | Status |
|------------|--------|--------|
| Connectivity metrics (largest component, global efficiency, avg shortest path) | `routeresilience/graph/metrics.py` | Done |
| Criticality — betweenness ranking, bridge roads, articulation junctions | `routeresilience/graph/criticality.py` | Done |
| Collapse simulation (smart-adversary node removal → decay curve) | `routeresilience/graph/collapse.py` | Done |
| Disaster scenarios (zone knockout → connectivity-loss metrics) | `routeresilience/graph/scenarios.py` | Done |
| Extended centralities — CFBC, α-centrality, k-core + overlap | `routeresilience/graph/criticality.py` | Planned |

**33 tests passing.** The road-extraction stages plug in by simply handing the engine a
`networkx.Graph` with `x`/`y` node coordinates and `length` edge weights — the engine
never changes.

## Quickstart

```bash
# 1. Install dependencies
python -m pip install networkx pytest

# 2. Run the demo (analyzes a synthetic city with a single river crossing)
python examples/demo.py

# 3. Run the test suite
python -m pytest -q
```

## Example output

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

## Repository structure

```
routeresilience/graph/   core graph resilience engine
examples/demo.py         runnable end-to-end demo
tests/                   test suite (33 tests)
docs/design/             design spec & implementation plan
assets/                  logo and visual assets
```

## Roadmap

- [x] **Graph resilience engine** — criticality (BC), collapse simulation, disaster scenarios
- [ ] Extended centralities — CFBC, α-centrality, k-core + critical-segment overlap (Jaccard)
- [ ] Real OSM ingestion → run on actual Bengaluru roads
- [ ] Occlusion-aware Transformer segmentation (connectivity-aware loss) + synthetic-occlusion robustness benchmark
- [ ] Topological reconstruction — MST + Disjoint-Set "healing" → routable graph
- [ ] Population / hospital impact overlay (people isolated, facilities cut off)
- [ ] Interactive map web app
- [ ] *Future scope:* resilience optimization — where to add a road for maximum resilience per rupee

## Technology stack

**Core engine (built & tested):** Python 3.11+ · NetworkX · pytest
**Road extraction:** PyTorch · U-Net / UNet++ / DeepLabV3+ / Transformer · connectivity-aware clDice loss · Albumentations · OpenCV
**Graph & geospatial:** NetworkX · PyTorch Geometric (GNN) · MST + Disjoint-Sets · scikit-image / FilFinder · OSMnx · Rasterio / GDAL
**Data:** Sentinel-2 · Resourcesat LISS-IV · Cartosat-3 · SpaceNet · DeepGlobe · OpenSatMap · OpenStreetMap
**App & viz:** Leaflet.js / Mapbox · Streamlit · QGIS · Matplotlib

## Team

**Web Hackers** — Bharatiya Antariksh Hackathon 2026

## Acknowledgements

Built for the **Bharatiya Antariksh Hackathon 2026**, a national innovation initiative
by the **Indian Space Research Organisation (ISRO)**, powered by **Hack2skill**.

Aligned with ISRO's **NNRMS** mandate — maximising the downstream utility of indigenous
Earth-observation satellites (Cartosat, Resourcesat LISS-IV) for GIS-based urban planning,
e-governance, and infrastructure/route verification.
