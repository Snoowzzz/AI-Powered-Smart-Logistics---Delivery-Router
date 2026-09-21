# AI-Powered Smart Logistics & Delivery Router

## 1. Project Overview

**Project Title:** AI-Powered Smart Logistics & Delivery Router

### Objective
Build a visual logistics optimizer that simulates a delivery vehicle finding an efficient route through a grid-based city.

The system should allow users to:
- Create a 2D city/grid environment.
- Place a **Depot/Start**, **Delivery Destination(s)**, and **Roadblocks/Obstacles**.
- Run **A\*** pathfinding to find an optimal route.
- Visualize the search process and final route.
- Compare A\* with **Dijkstra's Algorithm**.
- Introduce dynamic traffic conditions and route-cost changes.
- Recalculate the route when the environment changes.
- Display measurable performance metrics.

---

# 2. Core AI Algorithm

## A* Search Algorithm

A* is the primary AI/search algorithm.

### Formula

```text
f(n) = g(n) + h(n)
```

Where:

- `g(n)` = actual cost from the starting point to node `n`.
- `h(n)` = estimated cost from node `n` to the destination.
- `f(n)` = estimated total cost of the route through node `n`.

### Required Heuristics

Implement at least:

1. **Manhattan Distance**
2. **Euclidean Distance**

The GUI should allow the user to switch between the two heuristics and compare:

- Nodes explored
- Execution time
- Final path cost
- Final route

> Note: If all movement costs are positive and the heuristic is used in a standard A* setup, preserve correctness when comparing heuristics. The project should clearly document whether diagonal movement is enabled and whether the chosen heuristic remains admissible/consistent for that movement model.

---

# 3. Required Technology Stack

## Programming Language

- **Python 3.x**

## GUI

Recommended:

- **Pygame** — preferred for interactive grid visualization and animation.

Alternative:

- **Tkinter** — acceptable for a simpler implementation.

## Python Libraries

Minimum recommended dependencies:

```text
pygame
```

Optional/advanced:

```text
numpy
scikit-learn
```

Use `scikit-learn` only if the ML-enhanced heuristic extension is implemented.

Python standard-library modules that may be used:

```text
heapq
math
time
random
dataclasses
collections
typing
```

---

# 4. System Architecture

Organize the project into the following logical components:

```text
Project
│
├── Environment / Grid
│   ├── Grid generation
│   ├── Cell states
│   ├── Obstacles
│   ├── Traffic
│   └── Dynamic changes
│
├── Pathfinding Engine
│   ├── A*
│   ├── Manhattan heuristic
│   ├── Euclidean heuristic
│   └── Dijkstra
│
├── Dynamic Routing
│   ├── Traffic-aware costs
│   ├── Time-of-day simulation
│   └── Real-time replanning
│
├── Visualization
│   ├── Grid rendering
│   ├── Search animation
│   ├── Vehicle movement
│   └── Route display
│
├── Comparison / Metrics
│   ├── Execution time
│   ├── Nodes explored
│   ├── Path cost
│   └── Algorithm comparison
│
└── Documentation
    ├── README
    ├── Report
    └── Research references
```

---

# 5. Phase 1 — Build the 2D City Environment

## 5.1 Grid Map

Create a grid, for example:

```text
20 × 20
```

Represent the city using a 2D Python list.

### Suggested Cell States

| State | Meaning |
|---:|---|
| `0` | Normal road |
| `1` | Permanent obstacle/building |
| `2` | Depot / Start |
| `3` | Delivery destination |
| `4` | Traffic jam |
| `5` | Vehicle/current position (optional visual state) |

The exact internal representation may be changed if a cleaner object-oriented design is used.

## 5.2 User Interaction

The user should be able to:

- Place the depot.
- Place one or more delivery destinations.
- Add/remove obstacles.
- Add/remove traffic-jam cells.
- Reset the grid.
- Start the pathfinding simulation.

---

# 6. Phase 2 — Pygame Visualization

## 6.1 Grid Rendering

Use a clear color scheme, for example:

| Cell | Suggested Appearance |
|---|---|
| Normal road | White/light |
| Building/obstacle | Grey/dark |
| Depot | Green |
| Delivery destination | Red |
| Traffic jam | Orange |
| Open/frontier nodes | Light blue |
| Explored/closed nodes | Dark blue |
| Final path | Yellow |
| Vehicle | Distinct icon/color |

The exact colors are not mandatory; visual clarity is the priority.

## 6.2 Search Animation

During A* execution:

1. Show nodes added to the open/frontier set.
2. Show nodes that have been explored.
3. Animate the search.
4. When the destination is reached, reconstruct the path.
5. Animate the final route.

The user should be able to visually understand how A* searches the city.

---

# 7. Phase 3 — Implement Standard A*

## 7.1 Basic Requirements

Implement A* using a priority queue, preferably Python's:

```python
heapq
```

Each node should maintain enough information to reconstruct the final path.

At minimum track:

```text
g(n)
h(n)
f(n)
parent
```

## 7.2 Movement Costs

Recommended movement model:

```text
Horizontal move = 1.0
Vertical move   = 1.0
Diagonal move   = 1.41
```

Choose one of these designs and document it clearly:

- **4-directional movement:** up, down, left, right.
- **8-directional movement:** includes diagonals.

The heuristic must be selected consistently with the movement model.

## 7.3 Path Reconstruction

When the goal is reached:

```text
Goal → Parent → Parent → ... → Start
```

Reverse the sequence to obtain the final route.

---

# 8. Phase 4 — Heuristic Comparison

Implement:

## 8.1 Manhattan Distance

```text
h(n) = |x1 - x2| + |y1 - y2|
```

Best suited to a 4-directional grid with uniform movement costs.

## 8.2 Euclidean Distance

```text
h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)
```

Useful when diagonal movement is allowed.

## 8.3 GUI Heuristic Switcher

Provide a control such as:

```text
Heuristic:
[ Manhattan ▼ ]
[ Euclidean ]
```

The user should be able to run the same scenario using different heuristics.

Record:

- Execution time
- Nodes explored
- Path cost
- Path length
- Whether a valid route was found

---

# 9. Phase 5 — Dijkstra Comparison

Implement **Dijkstra's Algorithm** as a comparison algorithm.

Dijkstra can be viewed as pathfinding without a goal-directed heuristic:

```text
f(n) = g(n)
```

## Required Comparison

Run:

```text
A*
vs.
Dijkstra
```

on the same grid.

Compare:

| Metric | A* | Dijkstra |
|---|---:|---:|
| Execution time | | |
| Nodes explored | | |
| Path cost | | |
| Path length | | |

The comparison should demonstrate how heuristic guidance changes the search behavior.

Do not assume A* will always have lower measured execution time on every grid; report the actual measurements.

---

# 10. Phase 6 — Traffic-Aware Routing

Introduce dynamic route costs.

## 10.1 Traffic Cells

Traffic-jam cells should have a higher movement cost.

Example:

```text
Normal road = 1
Traffic road = 5
```

Therefore, the algorithm can choose a longer physical route if its total travel cost is lower.

Example:

```text
Short route:
Distance = 10
Traffic penalty = high
Total cost = 30

Longer route:
Distance = 14
Traffic penalty = low
Total cost = 14
```

The vehicle should choose the route with the lower total cost.

## 10.2 Important Design Principle

Do not simply change the heuristic arbitrarily to represent traffic.

Prefer:

```text
g(n) = accumulated travel cost
```

where the cost of entering a cell depends on its current traffic/weather condition.

Keep the heuristic as a lower-bound estimate of remaining cost when optimality is required.

---

# 11. Phase 7 — Time-of-Day Simulation

Add a simulated clock.

Example:

```text
08:00 AM → 08:01 AM → ...
```

or use accelerated simulation time.

## Rush Hour

Example trigger:

```text
5:00 PM
```

At rush hour:

- Increase traffic costs.
- Spawn traffic on selected roads.
- Increase the cost of existing traffic cells.
- Recalculate the route.

Example:

```text
Normal road cost = 1
Rush-hour traffic road cost = 5
```

The visualization should show the vehicle changing from a short congested route to an alternative lower-cost route when appropriate.

---

# 12. Phase 8 — Real-Time Replanning

This is the main advanced feature.

## Basic Version

Allow the user to create a new obstacle while the vehicle is moving.

Example:

```text
Vehicle → → → 🚧
```

If a roadblock appears on the current route:

1. Detect that the current route is blocked.
2. Stop/redirect the vehicle.
3. Set the vehicle's current position as the new start.
4. Recalculate the route.
5. Continue toward the destination.

## Advanced Version

Implement:

- **D* Lite**, or
- **Lifelong Planning A* (LPA*)**

These algorithms are designed for incremental replanning in changing environments.

### Recommended Project Progression

First implement:

```text
A*
↓
Dynamic obstacle detection
↓
A* replanning from current position
```

Then, if time permits:

```text
A*
↓
D* Lite / LPA*
```

This keeps the project achievable while leaving room for advanced research.

---

# 13. Phase 9 — Vehicle Simulation

Create a delivery vehicle that follows the calculated route.

The vehicle should:

1. Start at the depot.
2. Follow the calculated path cell by cell.
3. Update its current position.
4. Display movement visually.
5. Detect newly blocked cells.
6. Trigger replanning when necessary.
7. Continue until the destination is reached.

Optional:

- Vehicle speed
- Travel-time simulation
- Delivery completion animation

---

# 14. Phase 10 — Comparison Dashboard

Create a side panel displaying performance metrics.

## Required Metrics

### 1. Total Path Cost

The total weighted travel cost:

```text
Total Path Cost = Σ movement costs
```

### 2. Nodes Explored

Number of grid cells/nodes expanded during the search.

### 3. Execution Time

Measure using:

```python
time.perf_counter()
```

Report in milliseconds.

Example:

```text
Execution Time: 2.37 ms
```

### 4. Path Length

Number of cells or physical movement distance in the final path.

### 5. Route Status

Display:

```text
Route Found
```

or:

```text
No Route Available
```

---

# 15. Recommended Dashboard

Example UI:

```text
┌───────────────────────────────────┐
│       LOGISTICS AI DASHBOARD      │
├───────────────────────────────────┤
│ Algorithm: A*                     │
│ Heuristic: Manhattan              │
│                                   │
│ Path Cost:       34.0             │
│ Path Length:     28 cells         │
│ Nodes Explored:  96               │
│ Execution Time:  1.82 ms          │
│                                   │
│ Traffic:         Rush Hour        │
│ Replanning:      Enabled          │
└───────────────────────────────────┘
```

---

# 16. Algorithm Comparison Mode

Add a button such as:

```text
[ Compare Algorithms ]
```

The system should run the same environment using:

1. A* + Manhattan
2. A* + Euclidean
3. Dijkstra

Optional:

4. Traffic-Aware A*
5. D* Lite / LPA*

Display their measured results side by side.

Example:

```text
Algorithm        Nodes     Cost     Time
------------------------------------------------
A* Manhattan     85        32       1.7 ms
A* Euclidean     102       32       1.9 ms
Dijkstra         245       32       3.8 ms
```

These values are only an example; the actual project must display measured results.

---

# 17. Advanced Extension Options

Choose **one primary advanced feature** if the project needs a strong research component.

## Option A — Real-Time Replanning

### Technology
- D* Lite
- LPA*

### Idea
Reuse previous search information instead of performing a completely new search after every environmental change.

### Demonstration
Place a roadblock directly in front of the moving vehicle and show the system finding an alternative route.

### Research Reference
**D* Lite — Sven Koenig and Maxim Likhachev, AAAI.**

---

## Option B — Machine Learning-Enhanced Heuristic

Create a learned heuristic that estimates remaining travel cost.

### Possible Approach

1. Generate training routes using classical pathfinding.
2. Collect:
   - Start position
   - Goal position
   - Obstacles
   - Traffic conditions
   - Actual travel cost
3. Train a small ML model.
4. Use its prediction as an additional heuristic signal.
5. Compare it with standard A* heuristics.

### Suggested Technology

```text
scikit-learn
```

For a student project, start with:

- Linear Regression, or
- A small shallow neural network.

### Important Evaluation

Compare:

```text
Standard A*
vs.
ML-assisted A*
```

using:

- Nodes explored
- Execution time
- Path cost
- Route validity

### Research Direction

Look into **Neural A*** / differentiable path planning research, including work by Yonetani et al.

---

## Option C — Traffic & Cost-Aware Routing

Use changing conditions such as:

- Traffic
- Weather
- Road quality
- Time of day

to modify travel costs.

Example:

```text
Normal road = 1
Heavy traffic = 5
Rain = 2
Heavy traffic + rain = 7
```

The route optimizer then minimizes estimated travel cost rather than simply minimizing geometric distance.

This is the simplest advanced extension and is strongly recommended if development time is limited.

---

# 18. Optional Weather System

Add simulated weather conditions.

Example:

```text
Weather:
[ Clear ]
[ Rain ]
```

Rain can increase the cost of selected roads.

Example:

```text
Clear road cost = 1
Rain road cost = 2
```

The weather can be combined with traffic:

```text
Final Cost =
Base Road Cost
× Traffic Multiplier
× Weather Multiplier
```

---

# 19. Multiple Delivery Destinations

Optional advanced logistics feature:

```text
Depot
 ↓
Delivery 1
 ↓
Delivery 2
 ↓
Delivery 3
 ↓
Depot
```

The system can calculate routes between multiple destinations.

Possible future extension:

- Nearest-neighbor delivery ordering.
- Travelling Salesperson Problem (TSP) approximation.
- Vehicle capacity constraints.

Keep this separate from the core A* requirement so the project does not become unnecessarily complex.

---

# 20. Required User Controls

Recommended controls:

```text
[Set Depot]
[Set Delivery]
[Add Obstacle]
[Remove Obstacle]
[Add Traffic]
[Remove Traffic]

[Run A*]
[Run Dijkstra]
[Compare Algorithms]

[Manhattan]
[Euclidean]

[Start Vehicle]
[Pause]
[Reset]

[Enable Rush Hour]
[Enable Dynamic Obstacles]
```

Optional:

```text
[Enable Weather]
[Enable Replanning]
[Run D* Lite]
```

---

# 21. Recommended Project Folder Structure

```text
ai-smart-logistics-router/
│
├── main.py
├── requirements.txt
├── README.md
│
├── src/
│   ├── grid.py
│   ├── node.py
│   ├── astar.py
│   ├── dijkstra.py
│   ├── heuristics.py
│   ├── traffic.py
│   ├── replanning.py
│   ├── vehicle.py
│   ├── metrics.py
│   └── ui.py
│
├── tests/
│   ├── test_astar.py
│   ├── test_dijkstra.py
│   └── test_heuristics.py
│
├── research/
│   └── references.md
│
├── screenshots/
│
└── docs/
    └── project_report.md
```

For a smaller project, these modules may be combined initially and separated later.

---

# 22. Testing Requirements

Test at least these scenarios:

## Test 1 — Empty Grid

Expected:

- A* finds a direct/optimal route.
- Dijkstra finds the same optimal cost.

## Test 2 — Simple Obstacle

Create a wall and verify that the algorithm routes around it.

## Test 3 — No Possible Route

Completely block the destination.

Expected:

```text
No route found
```

## Test 4 — Traffic

Create a short route with heavy traffic and a longer route without traffic.

Verify that the traffic-aware cost function can choose the lower-cost route.

## Test 5 — Rush Hour

Increase traffic costs during simulated rush hour.

Verify that route selection can change.

## Test 6 — Dynamic Roadblock

Place a new obstacle on the vehicle's current route.

Expected:

```text
Detect blockage
→ Replan
→ Continue
```

## Test 7 — Algorithm Comparison

Run the same grid using:

```text
A*
Dijkstra
```

and record the metrics.

---

# 23. Performance Evaluation

The final report should include experimental comparisons.

Run multiple grid scenarios and record:

| Scenario | Algorithm | Heuristic | Nodes | Cost | Time |
|---|---|---|---:|---:|---:|
| Empty Grid | A* | Manhattan | | | |
| Empty Grid | A* | Euclidean | | | |
| Obstacles | A* | Manhattan | | | |
| Obstacles | A* | Euclidean | | | |
| Obstacles | Dijkstra | None | | | |
| Traffic | Traffic-A* | Selected | | | |
| Dynamic | Replanning | Selected | | | |

Use actual measured results.

---

# 24. Research References

The final project should cite relevant academic sources.

## Required/Recommended Topics

### A* Search

Research the original A* algorithm and heuristic search.

### D* Lite

**Sven Koenig and Maxim Likhachev — D* Lite, AAAI.**

Use this if implementing or discussing incremental replanning.

### Neural A*

Research:

**Path Planning using Neural A* Search — Yonetani et al.**

Use this if implementing the ML/neural extension.

### Traffic-Aware Routing

Research literature on:

- Dynamic route optimization
- Traffic-aware path planning
- Logistics optimization
- Weather-aware routing
- Intelligent transportation systems

The final report should distinguish clearly between published research and the project's own implementation.

---

# 25. Minimum Viable Project (Must Have)

To keep the project achievable, the following features are mandatory:

- [ ] Python implementation
- [ ] Pygame/Tkinter GUI
- [ ] 2D grid city
- [ ] Depot/start point
- [ ] Delivery destination
- [ ] Obstacles
- [ ] Working A*
- [ ] At least one valid heuristic
- [ ] Search animation
- [ ] Final route visualization
- [ ] Path cost calculation
- [ ] Nodes explored metric
- [ ] Execution-time metric
- [ ] Dijkstra comparison
- [ ] Basic project documentation

---

# 26. High-Scoring Features

Add these after the minimum version works:

- [ ] Manhattan vs Euclidean comparison
- [ ] Traffic-jam cells
- [ ] Traffic-aware route costs
- [ ] Simulated time of day
- [ ] Rush-hour traffic generation
- [ ] Moving delivery vehicle
- [ ] Dynamic roadblocks
- [ ] Automatic route replanning
- [ ] Comparison dashboard
- [ ] Multiple delivery destinations
- [ ] Weather simulation
- [ ] D* Lite / LPA*
- [ ] ML-enhanced heuristic

---

# 27. Recommended Implementation Order

Do **not** start with D* Lite or Machine Learning.

Build in this order:

```text
1. Create Python project
        ↓
2. Create 20×20 grid
        ↓
3. Render grid in Pygame
        ↓
4. Add mouse interaction
        ↓
5. Add depot and destination
        ↓
6. Add obstacles
        ↓
7. Implement A*
        ↓
8. Animate A* search
        ↓
9. Draw final route
        ↓
10. Add metrics
        ↓
11. Implement Dijkstra
        ↓
12. Add heuristic switcher
        ↓
13. Add traffic costs
        ↓
14. Add simulated rush hour
        ↓
15. Add moving vehicle
        ↓
16. Add dynamic roadblocks
        ↓
17. Add automatic replanning
        ↓
18. Add dashboard
        ↓
19. Add advanced algorithm
        ↓
20. Testing + screenshots + report
```

---

# 28. Three-Week Development Plan

## Week 1 — Foundation + Classical AI

### Goal
Get a fully working visual A* implementation.

Tasks:

- [ ] Set up Python environment.
- [ ] Create project structure.
- [ ] Create 20×20 grid.
- [ ] Build Pygame interface.
- [ ] Add depot.
- [ ] Add destination.
- [ ] Add obstacles.
- [ ] Implement A*.
- [ ] Implement heuristic function.
- [ ] Animate search.
- [ ] Display final route.

### Deliverable

A working visual A* city router.

---

## Week 2 — Intelligent Logistics

### Goal
Add real-world dynamic conditions.

Tasks:

- [ ] Implement Dijkstra.
- [ ] Add Manhattan/Euclidean switcher.
- [ ] Add comparison metrics.
- [ ] Add traffic cells.
- [ ] Add traffic-aware costs.
- [ ] Add simulated time.
- [ ] Add rush-hour event.
- [ ] Add vehicle movement.
- [ ] Add dynamic roadblocks.
- [ ] Add route replanning.

### Deliverable

A dynamic logistics simulation that can react to changing road conditions.

---

## Week 3 — Advanced AI + Documentation

### Goal
Make the project research-oriented and presentation-ready.

Tasks:

- [ ] Choose one advanced extension.
- [ ] Implement D* Lite/LPA* OR ML-enhanced heuristic.
- [ ] Improve dashboard.
- [ ] Run experiments.
- [ ] Collect performance data.
- [ ] Create comparison tables/graphs.
- [ ] Test edge cases.
- [ ] Capture screenshots.
- [ ] Write technical report.
- [ ] Add research references.
- [ ] Prepare final presentation/demo.

### Deliverable

A complete AI logistics optimizer with experimental results and documentation.

---

# 29. Final Demonstration Scenario

For the final presentation, demonstrate this sequence:

### Step 1
Create a city grid.

### Step 2
Place:

```text
Depot → Delivery
```

### Step 3
Add buildings/roadblocks.

### Step 4
Run standard A*.

Show:

```text
Search animation
Final route
Path cost
Nodes explored
Execution time
```

### Step 5
Run Dijkstra on the same environment.

Compare the metrics.

### Step 6
Enable traffic.

Show that the lowest-cost route can change when traffic penalties increase.

### Step 7
Start the delivery vehicle.

### Step 8
While the vehicle is moving, place a new roadblock directly on its route.

### Step 9
Show automatic replanning.

### Step 10
If implemented, demonstrate D* Lite/LPA* or the ML-enhanced heuristic.

This creates a clear progression:

```text
Classical AI
      ↓
A* Search
      ↓
Algorithm Comparison
      ↓
Cost-Aware Logistics
      ↓
Dynamic Environment
      ↓
Real-Time Replanning
      ↓
Advanced AI
```

---

# 30. Final Project Outcome

The completed system should demonstrate that AI can be used to optimize delivery routing under both static and dynamic conditions.

The project should combine:

```text
A*
+
Heuristics
+
Dijkstra
+
Graph/Grid Search
+
Traffic Costs
+
Visualization
+
Performance Measurement
+
Dynamic Replanning
```

with an optional advanced component:

```text
D* Lite / LPA*
OR
Machine Learning / Neural A*
```

The final result should be a **visual, measurable, interactive logistics simulation**, rather than only a command-line implementation of A*.
