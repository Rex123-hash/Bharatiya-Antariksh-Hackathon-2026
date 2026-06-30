# RouteResilience — Design Spec

**Hackathon:** Bharatiya Antariksh Hackathon 2026 (ISRO × Hack2skill)
**Challenge 4:** Route Resilience — Occlusion-Robust Road Extraction & Graph-Theoretic Criticality Analysis for Urban Mobility
**Date:** 2026-06-30
**Status:** Design approved; pending spec review

---

## 1. Summary

An end-to-end pipeline that turns fragmented satellite road masks into a connected
network graph, then ranks structural bottlenecks and simulates urban-collapse
scenarios. Delivered as an interactive map web app anchored on Bengaluru.

**Strategic wedge:** the graph-theoretic criticality + collapse-simulation engine
(Module 2) is the star and the primary differentiator. Road segmentation (Module 1)
is built to *serve* the graph — connectivity-first, not SOTA-chasing.

This maps directly to the problem statement, which frames fragmented masks as
"useless" for real-world use and defines the goal as transforming them into "a
mathematically continuous, weighted graph to identify systemic bottlenecks and
simulate urban collapse scenarios."

---

## 2. Problem statement alignment

| PS requirement | How this design addresses it |
|---|---|
| "See through" occlusions (canopy, shadow, cloud) | Module 1: context-aware segmentation with connectivity-aware loss |
| Topologically connected masks (not "broken") | Connectivity loss + vectorization that enforces a connected graph |
| Transform masks into a weighted graph | Bridge step: skeletonize → weighted nodes/edges |
| Identify systemic bottlenecks | Module 2: betweenness centrality, bridges, articulation points |
| Simulate urban collapse scenarios | Module 2: progressive removal → fragmentation curves; disaster overlays |
| Real-world applicability (disaster response, traffic sim) | Disaster scenario engine + interactive app |

---

## 3. Architecture

```
① DATA LAYER
   Bengaluru high-res optical tiles | OSM road network (ground truth) | Synthetic occlusion generator
        ↓
② MODULE 1 — Occlusion-robust segmentation  (supporting act)
   Context-aware encoder–decoder + connectivity-aware loss → topologically connected road mask
        ↓
③ BRIDGE — Vectorization
   Skeletonize mask → nodes (junctions) + edges (segments), weighted by length / travel-time / capacity
        ↓
④ MODULE 2 — Graph resilience engine  ★ THE STAR
   Criticality  |  Collapse simulation  |  Disaster scenarios
        ↓
⑤ DELIVERABLE — Interactive map web app
   pick tile → roads → graph → click/slide to collapse → live resilience metrics
```

---

## 4. Components

### 4.1 Data layer
- **Primary imagery (official):** Sentinel-2 (10 m), Resourcesat LISS-IV (5.8 m), and
  Cartosat-3 (high-res, provided during the finale). Anchored on Bengaluru.
- **Ground truth & pre-training (official):** OpenStreetMap road vectors plus SpaceNet,
  DeepGlobe, and OpenSatMap — auto-generated ground truth, no manual annotation.
- **Synthetic occlusion generator:** paints canopy / shadow / cloud patches onto
  clean tiles to produce paired occluded↔clean data. Enables a quantitative
  robustness ("recovery") metric that natural occlusion alone cannot provide.
  **Realism rules (not random rectangles):** shadows = elongated, semi-transparent
  dark blobs placed beside buildings with a consistent sun angle; canopy = irregular
  textured green blobs hugging roadsides with soft edges; clouds = large, feathered,
  semi-transparent patches. **Preferred:** lift real cloud/shadow/canopy mask shapes
  from other imagery and composite them, rather than synthesizing shapes from scratch.

### 4.2 Module 1 — Occlusion-robust segmentation (supporting act)
- **Transformer-based / attention** segmentation network, optimised for occlusion-recall
  (road recovery under shadow/canopy). U-Net / UNet++ / DeepLabV3+ are viable CNN baselines.
- **Connectivity-aware loss = clDice (centerline Dice) combined with Dice/BCE.**
  clDice is a published topology-preserving loss for thin connected structures (roads,
  vessels); it rewards keeping the centerline unbroken.
  - **Fallback (no new technique):** train with plain Dice/BCE, then reconnect breaks
    in post-processing (morphological closing + graph gap-filling that links nearby
    dangling road ends).
- Explicit non-goal: beating segmentation benchmarks. Bar = "clean enough to build a
  correct graph."

### 4.3 Bridge — Topological reconstruction (vectorization + healing)
- Skeletonize the predicted mask (scikit-image / FilFinder).
- **Topological "healing": Minimum Spanning Tree (MST) + Disjoint-Set (Union-Find)** to
  merge fragments into one connected, routable graph. The official **Connectivity Ratio**
  metric measures the LCC increase achieved by this healing step.
- Construct graph: nodes = junctions, edges = road segments.
- **Edge weights — length-first.** Default = road length (always available, reliable).
  - **Cheap upgrade, no external data:** map OSM road-type tags (`motorway`, `primary`,
    `residential`, …) → rough speed + lane count → estimated travel-time. Clearly
    labeled as an estimate.
  - Capacity stays optional; omitted if unreliable rather than faked.

### 4.4 Module 2 — Graph resilience engine (★ star)
- **Criticality (Gatekeeper Nodes):** betweenness centrality (+ planned CFBC, α-centrality,
  k-core) + bridges / articulation points → ranked "Gatekeeper Nodes" (single points of failure).
- **Collapse simulation:** progressively remove top-k critical elements → fragmentation
  curves (largest-connected-component %, global network-efficiency decay).
- **Disaster scenarios:** overlay a flood zone or blocked corridor → reroute on the
  graph.
  - **Floor metrics (graph-only, no external data, always delivered):** number of
    disconnected segments, drop in largest-connected-component %, increase in average
    shortest-path length.
  - **Impact overlay (enhancement):** population isolated (WorldPop / GHS-POP gridded
    population) and facilities cut off (OSM `amenity=hospital`). Both free; dropped
    without losing the core if data fights us.

### 4.5 Deliverable — Interactive map web app
- Select a tile → view extracted roads → flip to graph overlay (critical nodes
  highlighted) → click a node or drag a "remove top-k" slider → watch network split
  with live resilience metrics → switch disaster scenarios.
- Frontend tech (Streamlit/Gradio vs light React + Leaflet/Mapbox) decided at build
  time; both reach the same demo.

---

## 5. Success criteria

- **Module 1:** topology-aware score (e.g., APLS / connectivity metric) **plus** a
  synthetic-occlusion recovery number ("recovers X% of road length hidden under
  occlusion").
- **Module 2:** criticality ranking validated against the real OSM graph; collapse
  curves and scenario outputs reported quantitatively, not just visually.
- **Demo:** a judge can interactively trigger a collapse and read changed metrics in
  real time.

---

## 6. Scope boundaries (YAGNI — explicitly OUT)

- ❌ SAR / multimodal fusion
- ❌ Resilience *optimization* (tier 3) — appears in deck as "future scope" only
- ❌ Multi-city generality (Bengaluru only)
- ❌ Real-time / live traffic feeds
- ❌ Beating segmentation SOTA benchmarks

---

## 7. Two-deadline plan

- **Idea Submission (~July 1, 2026):** this design → submission deck + four text
  fields (brief, problem, tech stack, hackathon-experience). No code.
- **Grand Finale (Aug 6–7, 2026):** build Module 1 → bridge → Module 2 → app, in that
  dependency order, with Module 2 prioritized for polish.

---

## 8. Open items for build time

- Finalize public optical imagery source for Bengaluru.
- Choose segmentation backbone (clDice + Dice/BCE confirmed as the loss).
- Choose frontend stack (Streamlit/Gradio vs React + map library).
- Confirm WorldPop vs GHS-POP for the population overlay (both viable).
