# AI-Powered Smart Logistics & Delivery Router
## Final Project Handover — Current Checkpoint

**Current branch:** `main`  
**Current final application:** `app_4.0.py`  
**Application stack:** Python + Pygame  
**Routing algorithm:** A*  
**Grid:** 80 × 80  
**Map scale:** 2 km × 2 km → 25 m per cell

---

## 1. Project purpose

This project is a map-based logistics and delivery routing system built in Python and Pygame.

The system evolved from a basic A* demonstration into an interactive delivery router that can:

- route between named locations on the Livik map;
- use an 80 × 80 grid representation;
- distinguish highway and weak/muddy road cells;
- apply vehicle-specific road costs;
- let the user block multiple road cells before routing;
- build an ordered multi-stop delivery plan;
- animate A* search and the final route;
- report route and search statistics in the interface.

The project is designed to demonstrate both a practical logistics application and the underlying DSA concepts.

---

## 2. Current repository structure

The current project was cleaned up so the active project is easier to understand.

### Main application

`app_4.0.py`

This is the current final application file.

### Routing/map resources

- `PUBG_Mobile_Livik.jpg`
- `road_mask_80x80.txt`
- `weak_road_mask_80x80.txt`
- `location_access_points.txt`

### Documentation

- `README.md`
- `HANDOVER_FINAL.md`
- `PROJECT_TIMELINE_FINAL.md`

### Archive

Older experimental and development Python files were moved into `archive/` rather than being kept mixed with the final application.

The archived files exist as development history and are not the file to run for the final application.

---

## 3. Important project rules

### `app.py` baseline

The original `app.py` was intentionally kept as the untouched baseline during development.

The final active application is now `app_4.0.py`.

Do not casually merge old experimental code from the archive back into the final application.

### Current working branch

The completed work has been merged into `main`.

Future feature work should use a new branch created from `main`.

---

## 4. Map and grid representation

The Livik map image is displayed at:

```text
800 × 800 pixels
```

The logical routing grid is:

```text
80 rows × 80 columns
```

Therefore:

```text
CELL_SIZE = 800 / 80
          = 10 pixels per grid cell
```

The project treats the represented map area as approximately:

```text
2 km / 80 cells
= 0.025 km
= 25 m per cell
```

So each grid cell corresponds to approximately **25 metres of real-world distance**.

The routing system works with grid coordinates while the interface reports physical distances in metres.

---

## 5. Road representation

Two separate 80 × 80 road masks are used:

### Highway network

`road_mask_80x80.txt`

### Weak-road network

`weak_road_mask_80x80.txt`

The router combines these to determine traversable road cells.

The road masks are used for routing, but the clean normal map does not draw the masks directly over the map.

During A* visualization, search-state colors are shown instead.

---

## 6. Named locations

The project uses named locations rather than arbitrary mouse-selected grid cells.

Current named locations include:

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

Each named location has a manually selected access point stored in:

`location_access_points.txt`

This is important: the router does not guess the nearest road for a named location.

---

## 7. A* implementation

The core pathfinding algorithm is A*.

The implementation uses:

- `heapq` priority queue
- `g_score`
- `came_from`
- open set
- closed/explored set
- Euclidean heuristic
- 8-direction movement

Movement costs are:

```text
Straight movement = 1.0 cell unit
Diagonal movement = sqrt(2) cell units
```

The implementation also contains stale-priority-queue-entry protection so an outdated heap entry does not incorrectly terminate the search.

The goal is checked after the best current heap entry is removed.

---

## 8. Road weighting

The router distinguishes between highway and weak-road movement.

Highway multiplier:

```text
1.0
```

Weak-road multipliers are vehicle-dependent.

Current profiles:

```text
Car        = 1.5
Bike       = 1.2
Truck      = 2.2
Emergency  = 1.1
```

The selected vehicle affects the actual A* movement cost.

This means vehicle selection can influence which route A* chooses rather than merely changing a number after the route is already calculated.

---

## 9. Weighted-cost units

The A* weighted cost is stored in **grid-cell cost units**.

It is not intended to be interpreted directly as metres.

The physical map scale is:

```text
25 m per cell
```

Therefore the approximate weighted-distance equivalent is:

```text
weighted cell cost × 25 m
```

This is only a unit conversion.

It does not change which route is optimal because multiplying every route cost by the same positive constant does not change the minimum.

---

## 10. Heuristic verification

The current Euclidean heuristic is compatible with the weighted edge-cost model.

The reason is:

- straight highway movement has multiplier 1.0;
- weak-road multipliers are all at least 1.1;
- therefore each traversable edge costs at least its Euclidean geometric length.

So the Euclidean heuristic does not overestimate the remaining weighted cost under the current vehicle profiles.

The final verification tests also showed that the displayed weighted cost agrees with the internal weighted movement calculation, with small differences explained by displayed route distances being rounded to whole metres while the A* calculation retains the underlying cell/diagonal values.

---

## 11. Route analytics

The application reports:

- physical route distance;
- highway distance;
- weak-road distance;
- weighted route cost;
- explored A* nodes;
- number of stops for multi-stop routes.

The final UI uses:

### Route Planner

Displays:

```text
START
STOP 1
STOP 2
...
DESTINATION
```

### Route Summary

Displays KPI-style values and a Highway/Weak-road usage bar.

The Highway/Weak-road bar is intentionally preserved because it gives a quick visual breakdown of route composition.

---

## 12. Vehicle profiles

The interface supports:

```text
Car
Bike
Truck
Emergency
```

The vehicle can be changed before a route begins.

The selected vehicle is locked while A* search or path animation is running.

The current weak-road multiplier is displayed clearly in the Vehicle Profile section.

---

## 13. Interactive road blocking

Instead of hard-coded road restrictions, the user can dynamically modify the routing graph.

Workflow:

1. Click **BLOCK ROAD**.
2. Click road cells on the map.
3. Multiple road cells can be selected.
4. Click **CONFIRM BLOCKS**.
5. Confirmed blocked cells are excluded from A*.
6. The user can clear all blocks with **CLEAR ALL BLOCKS**.

The blocked-cell state is maintained separately from normal traversable road cells.

This is an important DSA feature because the user is dynamically changing which graph nodes/edges are available to the search.

---

## 14. Multi-stop routing

The application now supports an ordered delivery plan:

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

The user can select as many intermediate named locations as needed.

Each leg reuses the existing A* engine.

The system combines the resulting:

- distance;
- highway distance;
- weak-road distance;
- weighted cost;
- explored-node counts.

The Route Summary **STOPS** value counts only intermediate stops.

For example:

```text
Start
Stop 1
Stop 2
Stop 3
Destination
```

shows:

```text
STOPS = 3
```

The starting location and final destination are excluded from the stop count.

---

## 15. Search and animation visualization

The application provides visual feedback during A*.

The project uses:

```text
Blue   = open set
Purple = closed/explored set
Orange = current A* node
Yellow = final route
```

The clean map view does not permanently paint the road masks over the map.

---

## 16. Final UI structure

The final application uses a three-panel layout:

```text
LEFT                CENTER             RIGHT
----------------------------------------------------------------
Route Planner       800×800 Map         Vehicle Profile

Route Summary                            Road Blocking

                                         Route Controls
                                         Live Route Status
```

### Left

The left side is intentionally information-heavy because it is the user's route-planning and analytics area.

It contains:

- start;
- ordered stops;
- destination;
- route status;
- distance;
- weighted cost;
- explored nodes;
- stop count;
- highway/weak-road usage.

### Center

The map remains the main visual area at 800 × 800.

### Right

The right side contains operational controls:

- vehicle selection;
- weak-road multiplier;
- road blocking;
- multi-stop route controls;
- live route status.

The redundant workflow instructions were removed from the final layout to make room for useful live state.

---

## 17. Current verified example behavior

The project has already been tested with routes such as:

### Wengen → Hot Spring

Observed route characteristics included:

- highway distance around 1164 m;
- weak-road distance around 277 m;
- Car weak-road multiplier 1.5;
- weighted cost around 63.16 cell units.

### Wengen → Lupin Felt

Observed:

- highway around 25 m;
- weak road around 196 m;
- weighted cost around 12.74 cell units.

### Wengen → Blomster

Observed:

- highway around 614 m;
- weak road 0 m;
- weighted cost 24.56 cell units.

Vehicle tests also confirmed the configured multipliers:

```text
Car        1.50×
Bike       1.20×
Truck      2.20×
Emergency  1.10×
```

---

## 18. What is completed

### Core routing

- [x] 80 × 80 grid
- [x] A*
- [x] Euclidean heuristic
- [x] 8-direction movement
- [x] Highway/weak-road weighting
- [x] 25 m/cell scale

### Map data

- [x] Highway mask
- [x] Weak-road mask
- [x] Named locations
- [x] Manual access points

### Logistics features

- [x] Route analytics
- [x] Vehicle profiles
- [x] Interactive road blocking
- [x] Multiple blocked cells
- [x] Multi-stop routing
- [x] Stop counting

### UI

- [x] Integrated three-panel layout
- [x] Route Planner
- [x] Route Summary
- [x] Highway/Weak-road usage bar
- [x] Vehicle Profile
- [x] Road Blocking controls
- [x] Route Controls
- [x] Live Route Status

---

## 19. Remaining work

The major remaining technical work is:

### A* vs Dijkstra comparison

Implement Dijkstra using the same grid, road costs, blocked cells, vehicle profile, and endpoints so that the two algorithms can be compared fairly.

Useful comparison data:

- explored nodes;
- route distance;
- weighted cost;
- search behavior.

### Final testing

Run structured edge-case tests:

- same start and destination;
- blocked road requiring a detour;
- multiple blocked areas;
- no available route;
- all vehicle profiles;
- long multi-stop plans;
- reset behavior.

### Final documentation

Update `README.md` after the algorithm and test work are frozen.

### Final submission

Prepare the final project package, screenshots, demo flow, and DSA/viva explanation.

---

## 20. Recommended next branch workflow

From the clean `main` branch:

```bash
git switch main
git pull origin main
git switch -c astar-vs-dijkstra
```

All remaining algorithmic experiments should happen on a feature branch.

After successful testing:

```text
feature branch
    ↓
test
    ↓
commit
    ↓
merge into main
```

Do not modify `main` directly until a feature has been tested.

---

## 21. Final project story

The project progression can now be explained as:

```text
Basic A*
   ↓
Map-based A*
   ↓
80×80 grid
   ↓
Real road network
   ↓
Named locations + exact access points
   ↓
Weighted roads
   ↓
Route analytics
   ↓
Vehicle-specific costs
   ↓
Interactive road blocking
   ↓
Multi-stop routing
   ↓
Final three-panel logistics UI
   ↓
A* vs Dijkstra
   ↓
Final testing + submission
```

The main architectural principle throughout the project is:

> Keep the A* routing engine stable and build realistic logistics features around it.

That principle should continue for the remaining work.
