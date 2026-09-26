# AI Smart Logistics Router — Progress Note

## Project Goal

Build a working **AI-Powered Smart Logistics & Delivery Router** in Pygame that can use pathfinding to find and visualize efficient delivery routes.

The project started with an abstract city grid and is now being upgraded toward a **realistic map-based road router** after professor feedback.

---

## Current Status

**Completed through v0.4 — Core A* + animated search.**

Working features:

- Pygame environment
- Grid representation
- Depot / Start
- Delivery / Goal
- Obstacles
- Neighbor detection
- A* pathfinding
- Manhattan heuristic
- `g`, `h`, and `f` cost logic
- Path reconstruction
- Explored-cell visualization
- Step-by-step animated A* search

The current prototype successfully demonstrates the algorithm, but the next goal is to make the environment realistic rather than leaving it as a blank abstract grid.

---

## Important Project Direction Change

Professor feedback indicated that the blank-grid implementation is technically correct but looks more like a basic demonstration than a realistic logistics application.

The new direction is:

> **Use a real map image as the environment, represent the roads using a finer grid/road mask, allow selection of named locations, and run A* to find a road-constrained route between them.**

This keeps the existing A* work and changes the environment it operates on.

The current supplied map contains locations such as:

- Midstein
- Blomster
- Gass
- East Port
- Hot Spring
- Power Plant
- Aqueduct
- and other named areas

The exact set of locations used in the final demo can be limited to the most useful ones.

---

## Why This Is Still the Same Project

The underlying graph/pathfinding model remains:

```text
Cell = Node
Valid movement = Edge
g(n) = known cost from start
h(n) = estimated remaining cost
f(n) = g(n) + h(n)
came_from = parent information
A* = route search
```

The difference is that the graph is no longer an arbitrary empty grid.

Instead:

```text
Real map
   ↓
Grid representation
   ↓
Road cells = traversable
Non-road cells = unavailable
   ↓
A*
   ↓
Road route
```

This is a more realistic environment for the same algorithm.

---

## Current A* Understanding

### Heuristic

For the current 4-direction movement model:

```python
h(n) = |row1-row2| + |col1-col2|
```

This is Manhattan distance.

It is calculated from the **candidate node to the goal**.

### Cost model

Currently:

```text
Normal movement = 1
```

Therefore:

```text
g(n) = actual cost already travelled
h(n) = estimated cost remaining
f(n) = g(n) + h(n)
```

The priority queue uses the lowest `f` value to decide which candidate to explore next.

---

## Realistic Map Plan

### Stage 1 — Map Background

Load the supplied map image into Pygame and fit it to the application window.

### Stage 2 — Finer Grid

Overlay a finer grid on the map.

The purpose is to represent curved roads more accurately than the original 20×20 grid.

The grid cells become the pathfinding nodes.

### Stage 3 — Road Representation

For the first working version, manually define the important road cells or create a road mask.

Conceptually:

```text
ROAD       → traversable
NON-ROAD   → blocked
```

This avoids introducing computer vision unnecessarily.

### Stage 4 — Named Locations

Store important locations using map/grid coordinates:

```python
locations = {
    "Midstein": (...),
    "Blomster": (...),
    "Gass": (...),
}
```

The user can select a start and destination by name.

### Stage 5 — Map-Based A*

Convert the selected named locations into grid cells and run the existing A* engine.

The important difference is that `get_neighbors()` will only allow movement through valid road cells.

### Stage 6 — Route Visualization

During search:

- Show exploration over the map.
- Reconstruct the route when the destination is reached.
- Draw the final route in **yellow**.

### Stage 7 — Metrics

Display:

- Start
- Destination
- Path cost
- Nodes explored
- Execution time
- Route status

### Stage 8 — Vehicle

Animate a delivery vehicle along the final yellow route.

---

## Shortest vs Fastest Route

The first realistic version will calculate the **shortest road route**.

This means minimizing route distance / movement cost.

A true **fastest route** requires travel-time weights.

Later, roads can have different costs such as:

```text
Fast road      = 0.8
Normal road    = 1.0
Slow road      = 2.0
Traffic road   = 5.0
```

Then A* can minimize accumulated travel time rather than just distance.

This can become the traffic-aware logistics extension.

---

## Revised Milestones

### Milestone 1 — Basic Grid ✅

### Milestone 2 — City Setup ✅

### Milestone 3 — A* Pathfinding ✅

### Milestone 4 — Animated Search ✅

### Milestone 5 — Real Map Background ⏳

- Load map image
- Fit map to Pygame
- Establish map coordinates

### Milestone 6 — Road-Constrained Grid ⏳

- Finer grid
- Road cells
- Non-road cells
- Road-aware neighbor detection

### Milestone 7 — Named Locations ⏳

- Midstein
- Blomster
- Other selected major locations
- Start/destination selection

### Milestone 8 — Map-Based A* ⏳

- Run A* between named locations
- Animate search
- Draw final yellow route

### Milestone 9 — Metrics ⏳

- Route cost
- Nodes explored
- Execution time
- Route status

### Milestone 10 — Vehicle Simulation ⏳

- Vehicle follows yellow route

### Milestone 11 — Traffic / Travel-Time Routing ⏳

- Weighted roads
- Traffic costs
- Optional fastest-route behavior

### Milestone 12 — Dynamic Replanning ⏳

- Roadblocks
- Route recalculation
- Vehicle rerouting

### Milestone 13 — Final Demo / Polish ⏳

- Clean UI
- Demonstration scenario
- Screenshots
- Documentation

---

## Two-Week Immediate Target

The immediate target is a convincing map-based demo.

Minimum successful demo:

```text
Real map
   ↓
Select Midstein
   ↓
Select Blomster
   ↓
A* searches road cells
   ↓
Search animation
   ↓
Shortest route appears in yellow
   ↓
Metrics displayed
```

If time allows:

```text
   ↓
Vehicle follows route
   ↓
Traffic changes travel cost
   ↓
Route changes
```

Advanced algorithms such as D* Lite or ML are not priorities before this demo works.

---

## Current File

`app.py`

## Current Prototype

The current `app.py` is the working abstract-grid A* prototype.

The next code change will begin the **real-map version** rather than adding more features to the blank-grid version.

## Development Principle

The project should continue teaching DSA while being built.

New concepts should be introduced when they become necessary, especially:

- Graph representation
- Grid-to-map coordinate mapping
- Road masks
- Weighted graph edges
- Priority queues
- A* on constrained graphs
- Route reconstruction
- Metrics
- Vehicle path following

The project should remain practical and achievable within the available time.
