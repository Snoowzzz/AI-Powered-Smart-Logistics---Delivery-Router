# AI-Powered Smart Logistics & Delivery Router — Project Handover

## 1. Project

College DSA project:

**AI-Powered Smart Logistics & Delivery Router**

Technology:
- Python
- Pygame
- A* pathfinding
- 80×80 grid
- PUBG Mobile Livik map as the visual map

The project is intended to demonstrate practical DSA concepts through a logistics/delivery routing application.

---

## 2. IMPORTANT FILE SAFETY RULE

### Stable baseline
`app.py`

**DO NOT MODIFY `app.py`.**

It is the untouched/stable baseline.

### Current development file
The current work has been made in the existing **v0.8 80×80 named-location application**, not as a separate experimental branch file.

The current working file is:

`app_v0.8_80x80_named_locations.py`

The latest uploaded copy may have a generated/duplicate filename such as:

`app_v0.8_80x80_named_locations(2).py`

Treat the v0.8 80×80 named-location app as the current development source.

Do NOT casually create a second competing application or overwrite the stable `app.py`.

---

## 3. CURRENT PROJECT STATE

The application currently has:

### Map
- PUBG Mobile Livik map
- 800×800 display
- Original map image scaled to 800×800

### Grid
- 80×80 grid
- `CELL_SIZE = 10`
- Approximate real-world map size: 2 km
- Approximate scale: 25 m per grid cell

### Road layers
Two separate road masks are used:

- `road_mask_80x80.txt`
  - highway network
- `weak_road_mask_80x80.txt`
  - weak/muddy road network

The router can travel on:

```python
road_cells = highway_cells | weak_cells
```

The road masks are used internally by the routing algorithm.

The clean application does **not** draw all road cells over the map during normal routing.

---

## 4. ROAD NETWORK WORK

The highway network was manually created/refined.

The weak/muddy road network was also manually marked.

The highway network was verified as connected.

The weak-road layer contains roughly 500 marked cells.

Do not replace these masks with generated/guessed road data.

---

## 5. NAMED LOCATIONS

The application contains these 21 named Livik locations:

1. Wengen
2. Gass
3. Rose Farm
4. Iceborg
5. Lupin Felt
6. Hot Spring
7. Blomster
8. Gronhus
9. Crabgrass
10. East Port
11. Midstein
12. Fisherhus
13. Aqueduct
14. Reeds
15. Helle
16. Power Plant
17. Waterfall
18. Shipyard
19. Holdhus
20. Askehus
21. Lumber Yard

The locations are visual/reference points on the map.

They are NOT directly used as A* grid nodes.

---

## 6. EXACT LOCATION ACCESS POINTS

A separate manual marker workflow was created so the router does NOT guess the nearest road to a location.

Each named location has one manually selected exact road cell stored in:

`location_access_points.txt`

Current access points:

```text
Wengen=5,13
Lupin Felt=12,16
Gass=6,32
Rose Farm=3,51
Iceborg=10,68
Hot Spring=18,51
Blomster=21,16
Gronhus=22,35
Crabgrass=35,24
East Port=32,70
Midstein=42,49
Fisherhus=38,59
Aqueduct=54,11
Reeds=55,45
Helle=59,2
Power Plant=47,26
Waterfall=62,69
Shipyard=57,72
Holdhus=71,11
Askehus=75,26
Lumber Yard=65,52
```

Every access point must be an existing highway or weak-road cell.

Do not revert to nearest-road guessing unless there is a deliberate future reason.

---

## 7. LOCATION MARKER TOOL

A separate tool was created for manually assigning exact road access points:

`app_location_access_marker_v2.py`

Workflow:

1. Left-click a named location.
2. Left-click the exact road cell.
3. Press `C` to confirm/save that location.
4. Continue with the next location.
5. Only highway/weak-road cells are accepted.
6. `S` can save/screenshot.
7. `M` saves.
8. Right-click removes/reset access point.
9. ESC exits.

This tool was used to produce the current `location_access_points.txt`.

---

## 8. CURRENT ROUTING ALGORITHM

The current router uses **A***.

Libraries include:

```python
import pygame
import heapq
import math
import time
```

A* uses:
- `heapq` priority queue
- `g_score`
- `came_from`
- `open_set`
- `closed_set`
- Euclidean heuristic
- 8-direction movement

Directions include:
- horizontal
- vertical
- diagonal

Straight movement cost:

```python
1.0
```

Diagonal movement cost:

```python
math.sqrt(2)
```

---

## 9. WEIGHTED ROAD COST

The current weighted routing logic is:

### Highway

```python
road_multiplier = 1.0
```

### Weak road

```python
road_multiplier = 1.25
```

Movement cost is:

```python
cost = geometric_cost * road_multiplier
```

Therefore the router does not simply search for the shortest geometric path.

It can prefer a slightly longer highway route over a shorter route containing more weak-road travel.

This weighted-routing behavior has already been tested and works.

---

## 10. IMPORTANT A* DETAIL

The algorithm correctly stops when the goal is **popped from the priority queue**, not merely when it is first discovered.

Current logic includes stale heap-entry protection:

```python
if current_g != g_score.get(
    current_node,
    float("inf")
):
    return
```

Do NOT remove this.

The goal condition occurs after popping the best heap entry.

This was tested during debugging and is intentional.

---

## 11. CURRENT VISUAL DESIGN

The clean map visualization is considered a major success.

### Do NOT regress this.

The normal routing screen:

- does NOT draw all highway cells
- does NOT draw all weak-road cells
- keeps the Livik map visually clean

Search visualization:

- Blue = open set
- Purple = closed/explored set
- Orange = current A* node
- Yellow = final route

The final route is drawn as a connected yellow line through cell centers.

It is NOT drawn as hundreds of yellow road blocks.

This clean route-line presentation was intentionally chosen because it looks much more like a real map-routing application.

---

## 12. START / DESTINATION BEHAVIOR

User interaction:

1. Click a named location.
2. First clicked location becomes START.
3. Second clicked location becomes DESTINATION.
4. A* begins automatically.
5. Search animates.
6. Final route animates.
7. After completion, another location can be clicked to start a new route.
8. Right-click resets the route.

The exact road cells come from:

`LOCATION_ACCESS`

loaded from:

`location_access_points.txt`

---

## 13. CURRENT STATS BEFORE STAGE 1

The original/current v0.8 application already displayed:

- number of explored nodes
- physical route distance

The relevant existing display was:

```text
Explored: ...
Route: ... m
```

This is the baseline that Stage 1 expands.

---

# 14. STAGE 1 — ROUTE ANALYTICS

### Goal

Improve the route statistics without changing the underlying routing behavior.

The intended Stage 1 analytics are:

- Explored nodes
- Physical route distance
- Highway distance
- Weak-road distance
- Weighted route cost

Example:

```text
Explored: 184
Distance: 1425 m
Weighted Cost: 57.32
Highway: 1080 m
Weak Road: 345 m
```

### Important

The current development source should receive these changes directly.

Do NOT make the project depend on a separate simplified Stage 1 application.

A handoff/test file may be generated temporarily, but the actual project source remains the v0.8 application.

---

## 15. SEARCH TIME — DO NOT MEASURE INCORRECTLY

The search is intentionally animated.

Current search animation delay is approximately:

```python
SEARCH_DELAY = 0.08
```

Therefore, simply measuring from the beginning of the animation to the end would mix:

- actual algorithm computation
- visualization delay

That would not be a clean DSA performance measurement.

Proper search execution timing should be added later when implementing the A* vs Dijkstra comparison.

---

# 16. PLANNED FUTURE STAGES

These are planned, not all completed.

Do not assume they already exist.

## Stage 1 — Route Analytics
Current stage.

Add:
- explored nodes
- physical distance
- highway distance
- weak-road distance
- weighted cost

---

## Stage 2 — Vehicle Profiles

Planned vehicle profiles:

### Car
Weak-road multiplier around:

```text
1.25
```

### Truck
Weak-road multiplier around:

```text
1.50
```

### Emergency
Weak-road multiplier around:

```text
1.10
```

Highway remains:

```text
1.00
```

The exact final values can be adjusted during implementation/testing.

The UI should eventually allow selecting the vehicle.

Do not implement this until Stage 1 is stable.

---

## Stage 3 — Road Restrictions

Possible planned features:

- blocked road
- restricted road
- vehicle-specific restrictions

This must be implemented carefully because it changes graph connectivity and may create no-route cases.

---

## Stage 4 — Algorithm Comparison

Planned algorithms:

- A*
- Dijkstra

Compare measurable DSA metrics such as:

- nodes explored
- execution time
- route cost
- route distance

The timing should measure actual algorithm execution rather than animation delay.

---

## Stage 5 — UI Customization

Possible additions:

- vehicle selector
- algorithm selector
- cleaner route information panel
- legend
- route summary
- improved status area

Do not redesign the UI before the core functionality is stable.

---

## Stage 6 — Testing

Planned test cases:

1. Highway-only route
2. Route containing weak roads
3. Weighted-routing tradeoff
4. Different vehicle profiles
5. A* vs Dijkstra
6. Blocked road
7. Same source/destination
8. No-route scenario

Record actual results rather than inventing expected numbers.

---

## Stage 7 — Submission Package

Planned documentation:

- Project overview
- Problem statement
- DSA concepts
- Graph representation
- Weighted graph explanation
- A* pseudocode
- Algorithm complexity
- Architecture
- Flowchart
- Feature list
- Screenshots
- Test results
- Limitations
- Future scope
- Viva questions and answers

---

# 17. OPTIONAL FUTURE FEATURE

A possible extra feature discussed:

### Delivery Priority

Possible levels:

- Normal
- Urgent
- Emergency

This should only be added after the main stages are stable.

It should not be allowed to destabilize the core routing system.

---

# 18. WORKING STYLE / RULES FOR FUTURE CHAT

The user prefers:

- Complete replacement code rather than instructions to manually edit many scattered sections.
- Exact file names.
- Exact placement.
- Minimal unnecessary changes.
- Testing after each milestone.
- Preserve already-working behavior.
- No casual refactoring.
- No changes to `app.py`.
- Do not simplify the existing 1,100+ line application into a much smaller example unless explicitly requested.
- Build on the current application.
- One stage at a time.
- If possible, produce a ready-to-run `.py` file instead of asking the user to manually insert many code fragments.

The user is comfortable with Python but is still learning DSA, so explain the DSA reason briefly while keeping implementation practical.

---

# 19. CURRENT PRIORITY

The immediate priority is:

**Finish and verify Stage 1 Route Analytics.**

After it is tested and confirmed:

**Stage 2 — Vehicle Profiles**

Then continue through the planned stages gradually.

There is no need to rush all features into one night.

The project submission is coming up, but the work should remain stable and testable.

---

# 20. DO NOT LOSE THESE PROJECT PRINCIPLES

1. `app.py` is the untouched baseline.
2. Current development is in the v0.8 80×80 named-location application.
3. Keep the exact manually selected access points.
4. Keep the highway and weak-road masks.
5. Keep weighted A*.
6. Keep the clean map.
7. Keep the animated open/closed/current visualization.
8. Keep the yellow route line.
9. Do not bring back huge road-cell overlays into the normal routing view.
10. Do not remove stale heap-entry protection.
11. Do not replace exact access points with nearest-road guessing.
12. Make one milestone at a time.
13. Test before moving to the next milestone.
14. Prefer complete ready-to-run files over large manual edit instructions.

---

## Current status

**Core routing:** WORKING

**Named locations:** WORKING

**Exact access points:** WORKING

**Highway + weak roads:** WORKING

**Weighted A*:** WORKING

**Clean route visualization:** WORKING

**Stage 1 Route Analytics:** IN PROGRESS / VERIFY

**Stage 2 Vehicle Profiles:** NOT STARTED

**Stage 3 Road Restrictions:** NOT STARTED

**Stage 4 A* vs Dijkstra:** NOT STARTED

**Stage 5 UI customization:** NOT STARTED

**Stage 6 Testing:** NOT STARTED

**Stage 7 Submission package:** NOT STARTED
