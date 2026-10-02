# AI-Powered Smart Logistics & Delivery Router
## Project Timeline — From A* Prototype to Final Application

This timeline records how the project evolved into the current `app_4.0.py` application.

---

## Phase 0 — Project setup and baseline

### Goal

Establish the project structure and create a safe baseline before modifying the routing system.

### Work completed

- Initial Python/Pygame application established.
- Basic map-based routing experiment created.
- `app.py` became the untouched baseline.
- Development work was separated into Git branches.

### Result

There was a stable starting point that could be preserved while later routing experiments continued.

---

## Phase 1 — Initial A* implementation

### Goal

Move from a simple map interaction to an actual DSA-based route search.

### Work completed

- Grid representation introduced.
- A* implemented using `heapq`.
- `g_score` used to track best-known path cost.
- `came_from` used to reconstruct the final path.
- Euclidean heuristic introduced.
- 8-direction movement added.
- Straight and diagonal movement costs established.
- Search progress visualized.

### Result

The application could calculate and animate A* routes on the map.

---

## Phase 2 — Real map road representation

### Goal

Make the graph represent roads instead of treating the whole image as equally traversable terrain.

### Work completed

- Highway cells manually represented in an 80 × 80 mask.
- Highway mask refined to the 80 × 80 grid.
- Road visualization/debugging tools were used during development.
- The routing graph was restricted to the road network.

### Result

A* began behaving as a road router rather than a generic grid pathfinder.

---

## Phase 3 — Named locations

### Goal

Replace arbitrary start/end clicks with recognizable delivery locations.

### Work completed

Named locations were added, including:

- Wengen
- Gass
- Rose Farm
- Iceborg
- Lupin Felt
- Hot Spring
- Blomster
- Gronhus
- Crabgrass
- East Port
- Midstein
- Fisherhus
- Aqueduct
- Reeds
- Helle
- Power Plant
- Waterfall
- Shipyard
- Holdhus
- Askehus
- Lumber Yard

### Important improvement

Exact manually selected access points were stored in:

`location_access_points.txt`

The router therefore does not rely on nearest-road guessing.

### Result

The user can think in terms of actual locations rather than grid coordinates.

---

## Phase 4 — Highway + weak-road network

### Goal

Make the map more realistic by distinguishing major roads from weaker roads.

### Work completed

A second mask was introduced:

`weak_road_mask_80x80.txt`

The router now uses:

```text
Highway network
+
Weak-road network
```

The normal map remains visually clean; the masks are used by the routing logic rather than permanently covering the map.

### Result

The route can contain different road categories.

---

## Phase 5 — Weighted road costs

### Goal

Make road quality affect the A* objective.

### Work completed

Highway cost:

```text
1.0
```

Weak-road cost was increased:

```text
1.25
```

during the first weighted-road stage.

A* movement cost began accounting for both:

- geometric movement cost;
- road-type multiplier.

### Result

The router no longer optimized only for physical route length. It began considering route quality.

---

## Phase 6 — Route analytics

### Goal

Expose useful information about what A* calculated.

### Work completed

The application added:

- explored node count;
- physical route distance;
- highway distance;
- weak-road distance;
- weighted route cost.

### Result

The application became useful not only for finding a route but also for explaining the behavior of A*.

---

## Phase 7 — Vehicle profiles

### Goal

Make the weighted road model depend on the delivery vehicle.

### Final multipliers

```text
Car        highway 1.0   weak road 1.5
Bike       highway 1.0   weak road 1.2
Truck      highway 1.0   weak road 2.2
Emergency  highway 1.0   weak road 1.1
```

### Work completed

- Vehicle selection added to the UI.
- Vehicle choice connected directly to A* movement cost.
- Vehicle selection locked while routing is running.
- Multiplier displayed in the interface.

### Result

Different vehicles can legitimately prefer different routes because the weighted graph changes with the vehicle.

---

## Phase 8 — Route Details interface

### Goal

Make route statistics accessible without destroying the map view.

### Work completed

- Separate Route Details display introduced.
- Popup made draggable.
- Popup height reduced.
- Interface tested repeatedly.
- Popup eventually identified as too intrusive because it covered useful map space.

### Result

The popup concept was useful temporarily but was later replaced by a more integrated layout.

---

## Phase 9 — Interactive road blocking

### Goal

Replace artificial predefined restrictions with a user-controlled graph modification feature.

### Design

The user can:

1. click **BLOCK ROAD**;
2. select road cells;
3. select multiple cells;
4. click **CONFIRM BLOCKS**;
5. run A*.

Blocked cells are excluded from the A* search.

### Additional behavior

- pending selections;
- confirmed blocked cells;
- clear-all control;
- blocked start/goal protection;
- blocked cells shown on the map.

### Result

The graph can be modified interactively before a route is calculated.

This is a strong DSA demonstration because A* must adapt to the changed graph.

---

## Phase 10 — Multi-stop routing

### Goal

Support a delivery journey with multiple intermediate stops.

### Desired model

```text
Start
  ↓
Stop 1
  ↓
Stop 2
  ↓
Stop 3
  ↓
Destination
```

### Work completed

- Multi-stop mode added.
- Ordered stop selection added.
- Multiple intermediate named locations supported.
- Final destination selected separately.
- Each leg reuses the existing A* engine.
- Leg statistics accumulated into a total.
- Final dashboard count changed from `LEGS` to `STOPS`.

### Stop-count definition

The dashboard counts only intermediate delivery stops.

Example:

```text
Start → A → B → C → Destination
```

reports:

```text
STOPS = 3
```

### Result

The application moved from a simple point-to-point router into a delivery itinerary planner.

---

## Phase 11 — Window and layout experimentation

### Goal

Find a practical interface size without disturbing the 80 × 80 map.

### Experiments

Larger map/window versions were tested:

- 1100 × 1100
- 950 × 950

These versions caused route-animation alignment issues.

### Decision

The map was returned to:

```text
800 × 800
```

The map/grid calculation was kept stable.

### Result

The map remained predictable while UI space was added around it instead of enlarging the routing canvas.

---

## Phase 12 — Three-panel UI redesign

### Goal

Use the available window area more intelligently.

### Final concept

```text
LEFT                  CENTER                 RIGHT
---------------------------------------------------------
Route Planner         800×800 Map             Vehicle
Route Summary                                 Road Blocking
                                              Route Controls
                                              Live Status
```

### Left side

The left side became the main information panel.

It contains:

- Start;
- Stops;
- Destination;
- route status;
- distance;
- weighted cost;
- explored nodes;
- stop count;
- Highway/Weak-road usage bar.

### Right side

The right side became the operations panel.

It contains:

- Vehicle Profile;
- weak-road multiplier;
- Road Blocking controls;
- Multi-stop route controls;
- Live Route Status.

### Important UI decision

The Highway/Weak-road usage bar was retained because it gives a quick visual representation of road composition.

The redundant workflow text was removed from the final UI to give more room to useful controls and live status.

### Result

The application now uses the space around the map as a proper logistics dashboard rather than relying on a floating popup.

---

## Phase 13 — Weighted-cost verification

### Goal

Verify that the reported weighted cost is consistent with the cell scale and vehicle multipliers.

### Scale

```text
2 km / 80 cells = 25 m per cell
```

### Movement cost

```text
Straight = 1.0 cell unit
Diagonal = sqrt(2) cell units
```

### Vehicle weighting

```text
Car        = 1.5 on weak roads
Bike       = 1.2 on weak roads
Truck      = 2.2 on weak roads
Emergency  = 1.1 on weak roads
```

### Verification examples

A clean highway-only route gave:

```text
614 m / 25 m ≈ 24.56 cell units
```

matching the application's weighted cost.

Mixed-road routes showed the expected increase according to the vehicle multiplier.

### Result

The weighted-cost calculations were considered internally consistent and the routing/cost engine was frozen.

---

## Phase 14 — Final repository cleanup

### Goal

Prevent the project from looking like a collection of unrelated experiments.

### Work completed

Old experimental Python files were moved into:

`archive/`

The active repository now keeps:

- `app_4.0.py`
- routing/map resources
- documentation
- archive of earlier versions

Project-detail documents that were no longer relevant were removed.

### Result

The repository now has a clearer distinction between the final application and development history.

---

## Current checkpoint

### Completed

- [x] A* implementation
- [x] 80 × 80 grid
- [x] 8-direction movement
- [x] Real road network
- [x] Highway mask
- [x] Weak-road mask
- [x] Named locations
- [x] Manual access points
- [x] Weighted road costs
- [x] Route analytics
- [x] Vehicle profiles
- [x] Interactive road blocking
- [x] Multiple blocked cells
- [x] Multi-stop routing
- [x] Final three-panel UI
- [x] Highway/Weak-road usage bar
- [x] Weighted-cost verification
- [x] Repository cleanup

---

## Remaining milestones

### Next technical milestone

**A* vs Dijkstra comparison**

Use the same:

- map;
- road graph;
- vehicle profile;
- blocked cells;
- start;
- destination.

Compare:

- explored nodes;
- route distance;
- weighted cost;
- search behavior.

---

### After that

**Final testing**

Test:

- normal single route;
- all four vehicles;
- blocked-road detours;
- multiple blocks;
- no-route situations;
- multi-stop plans;
- reset behavior;
- edge cases.

---

### Final documentation

Update `README.md` so it describes the final implementation rather than the earlier development stages.

---

### Final submission preparation

Prepare:

- final screenshots;
- demo sequence;
- DSA explanation;
- A* complexity discussion;
- A* vs Dijkstra results;
- final Git history;
- submission-ready folder.

---

## Overall project evolution

```text
A* prototype
      ↓
Grid-based routing
      ↓
Road-constrained routing
      ↓
Named locations
      ↓
Highway + weak roads
      ↓
Weighted costs
      ↓
Route analytics
      ↓
Vehicle profiles
      ↓
Interactive road blocking
      ↓
Multi-stop deliveries
      ↓
Three-panel logistics dashboard
      ↓
A* vs Dijkstra
      ↓
Final validation
      ↓
Submission
```

The current project is therefore no longer just an A* demonstration. It is an interactive logistics routing system built around A* with a user-modifiable road graph, vehicle-dependent costs, multi-stop delivery planning, and route analytics.
