# Route Resilience design

Bharatiya Antariksh Hackathon 2026 (ISRO and Hack2skill), Challenge 4.
Team Web Hackers.

## Overview

Route Resilience takes occluded optical satellite imagery of a city and produces a
connected road-network graph, then analyses that graph to find the junctions whose
failure would break urban mobility and to simulate what happens during a disaster.

The work has two halves. The first recovers a connected road mask from imagery where
tree canopy, building shadows and cloud have hidden parts of the road. The second turns
that mask into a weighted graph and runs the resilience analysis on it.

Most of our effort goes into the second half. Road segmentation is a crowded research
area, and we do not try to beat the best models there; we only need a mask clean enough
to build a correct graph. The graph analysis is where the project is different, and it
is what the demo is built around. We anchor the work on Bengaluru, the city named in the
problem statement.

## How it maps to the problem statement

| Requirement | How we address it |
|---|---|
| See through occlusions (canopy, shadow, cloud) | Transformer-based, occlusion-aware segmentation with a connectivity-aware loss |
| Produce connected masks, not broken ones | Connectivity loss during training plus MST/disjoint-set healing during vectorization |
| Turn masks into a weighted graph | Skeletonize, then build nodes (junctions) and weighted edges (segments) |
| Identify systemic bottlenecks | Betweenness centrality, bridges and articulation points |
| Simulate urban-collapse scenarios | Progressive node removal and disaster-zone overlays |
| Be useful in practice (disaster response, traffic) | Disaster scenario engine and an interactive map app |

## Pipeline

```
Imagery + ground truth  ->  Road extraction  ->  Topological reconstruction
                                                          |
                                                          v
                            Interactive map  <-  Graph resilience engine
```

## Road extraction

A Transformer or attention-based segmentation network, optimised for recovering roads
that are hidden under shadow and canopy (occlusion-recall). U-Net, UNet++ and DeepLabV3+
are reasonable CNN baselines if needed.

The loss is clDice (centerline Dice) combined with Dice or BCE. clDice is a published
loss for thin connected structures such as roads and blood vessels, and it rewards
keeping the centerline of a road unbroken. If that proves fiddly, the fallback is to
train with plain Dice/BCE and reconnect small breaks afterwards with morphological
closing and a gap-filling step that links nearby dangling road ends.

The goal here is a mask that is clean enough to build a correct graph, not a record
segmentation score.

## Topological reconstruction

The predicted mask is skeletonized (scikit-image or FilFinder) and then "healed" into a
single connected, routable graph using a Minimum Spanning Tree over the fragments and a
Disjoint-Set (Union-Find) structure to merge them. The challenge's Connectivity Ratio
metric measures exactly this: how much the largest connected component grows after the
healing step.

Edges are weighted by road length, which is always available. As a cheap improvement
that needs no extra data, OSM road-type tags (motorway, primary, residential, and so on)
can be mapped to rough speeds and lane counts to estimate travel time. We label that as
an estimate. Capacity is optional and is left out rather than faked if it is unreliable.

## Graph resilience engine

This part is already built and tested. It works on a NetworkX graph and has four pieces:

- Criticality. Ranks junctions by betweenness centrality (the "Gatekeeper Nodes"), and
  finds bridges and articulation points, which are the structural single points of
  failure. Current-flow betweenness, alpha-centrality and k-core are planned additions
  so the measures can be compared, as the challenge expects.
- Collapse simulation. Removes the most critical node repeatedly, recomputing
  betweenness each step, and records how connectivity decays (largest-component size and
  global efficiency).
- Disaster scenarios. Disables every road with an endpoint inside a flood or blocked
  zone, then reports the connectivity loss: edges cut, number of disconnected
  sub-networks, and the size of the largest remaining component.
- Impact overlay (optional). Adds population isolated (WorldPop or GHS-POP) and
  facilities cut off (OSM hospitals). The graph-only metrics above always work; the
  overlay is dropped if the data proves hard to get, without losing the core result.

## Datasets

Primary imagery: Sentinel-2 (10 m), Resourcesat LISS-IV (5.8 m), and Cartosat-3
(high-resolution, provided during the finale). Ground truth and pre-training:
OpenStreetMap road vectors, SpaceNet, DeepGlobe and OpenSatMap. OSM gives auto-generated
ground truth, so there is no manual annotation step.

For evaluating occlusion-robustness we also generate synthetic occlusion: realistic
shadow, canopy and cloud shapes composited onto clean tiles, which gives paired
occluded and clean images and a clear before/after recovery number. The shapes are made
to look like real occlusion (elongated shadows beside buildings, irregular canopy along
roadsides, soft-edged clouds), or lifted directly from real imagery, rather than being
random rectangles.

## Evaluation

These follow the challenge's official evaluation parameters.

- IoU and Dice, with attention to occlusion-recall (roads recovered under shadow).
- Generalisation across dense-urban, forested-suburban and rural terrain.
- Length-complete / relaxed IoU, using a 3 to 5 pixel tolerance buffer.
- Connectivity Ratio: the increase in the largest connected component after healing.
  The engine computes this today.
- Topological Accuracy: average path-length error against OSM. The engine computes this
  today.
- Resilience: connectivity loss, rerouting and travel-time increase as Gatekeeper Nodes
  fail.

## Out of scope

We are deliberately not doing SAR or multimodal fusion, resilience optimization
(suggesting where to add roads), multi-city generalisation, or live traffic feeds, and
we are not trying to beat segmentation benchmarks. Resilience optimization is mentioned
in the deck only as future work.

## Status and timeline

The graph resilience engine is built and covered by an automated test suite. For the
idea-submission stage (around 1 July 2026) the deliverable is the deck and the written
fields, not running code. For the finale (6 to 7 August 2026) the plan is to build the
extraction model, the healing step and the app on top of the existing engine, in that
order, keeping the engine as the most polished part.

The approach aligns with ISRO's NNRMS mandate: making better use of indigenous
Earth-observation satellites (Cartosat, Resourcesat LISS-IV) for GIS-based urban
planning and infrastructure verification.
