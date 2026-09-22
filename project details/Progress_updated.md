# AI Smart Logistics Router — Progress Note

## Project Goal
Build a working **AI-Powered Smart Logistics & Delivery Router** in Pygame that can model a city grid, place a depot and delivery destination, handle obstacles, and eventually use pathfinding algorithms such as A* to find and visualize efficient delivery routes.

---

## Current Status

**Milestone 2 in progress: Interactive city/grid setup is working.**

The basic Pygame grid is complete, and the application can now represent the main elements needed before pathfinding:

- Depot / Start
- Delivery / Goal
- Obstacles / Blocked cells
- Valid neighboring cells for pathfinding

The project is currently being developed toward a **working, presentable prototype first**, rather than spending too much time on refinement early.

### Important learning/project constraint

The DSA concepts used in this project should be **taught and understood while building**, not skipped simply because some concepts may already be familiar from Python.

I am currently learning DSA, so the project should introduce concepts such as:
- Graphs / nodes / edges
- Priority queues / heaps
- A* search
- Heuristics
- Path reconstruction
- Dijkstra's algorithm

at the point where they are needed.

At the same time, development should be **efficient and practical** because the immediate goal is to have a **decent working model ready to demonstrate to the professor around October 1st–8th**. The first target is functionality and a clear demonstration; refinement and advanced features can come afterward.

---

## Setup Completed

- Created GitHub repository
- Linked GitHub with VS Code
- Installed Pygame successfully
- Created `app.py`

---

## What We Have Built

### Basic Grid

- 800×800 Pygame window
- 20×20 city grid
- Each cell is 40×40 pixels
- Mouse clicks convert screen coordinates to `(row, col)`
- Basic Pygame event loop
- 60 FPS refresh
- Grid cells are represented using `(row, col)` coordinates

### City Elements

The application now supports:

- **Depot / Start** — selected using `1`
- **Delivery / Goal** — selected using `2`
- **Obstacles** — selected using `3`
- **Reset map** — `R`

Obstacles are stored separately from the start and goal:

```python
blocked_cells   # obstacles
start           # depot
goal            # delivery
```

The start and goal cannot remain blocked, and obstacles can be toggled on/off.

### Neighbor Detection

Added a `get_neighbors(cell)` function.

It checks the four possible directions:

- Up
- Down
- Left
- Right

and returns only cells that:

- Are inside the grid
- Are not blocked by an obstacle

This is the first step toward treating the city grid as a graph for pathfinding.

---

## Concepts Understood

### Pygame / Project Structure

- `pygame.init()`
- Pygame window creation
- `while running` game loop
- Event handling
- Keyboard and mouse input
- Nested loops for drawing the grid
- Screen coordinates → grid coordinates
- Using a `set` for blocked cells

### Data Structures / DSA

Current understanding includes:

- A grid can be treated as a **graph**
- Each cell can represent a **node**
- Valid movement between cells represents an **edge**
- Obstacles represent unavailable nodes
- `set` is useful for fast blocked-cell membership checks
- A neighbor function determines which nodes can be reached from a cell

DSA knowledge should continue to be developed alongside the project rather than assuming advanced DSA knowledge.

---

## Debugging / Testing

A temporary debug print was used to verify `get_neighbors()` and the blocked-cell state.

The observed behavior was correct: the debug output occurred before the current mouse click modified the obstacle set, so the next click displayed the updated state.

This helped verify the event-handling order and that neighbor detection responds to obstacles correctly.

The temporary debug output should be removed before continuing with the main implementation.

---

## Current Development Strategy

Because the project needs a **working model soon**, development will prioritize:

1. Core functionality
2. Clear visualization
3. Demonstrable pathfinding
4. Basic metrics
5. Comparison with another algorithm
6. Refinement / polish
7. Advanced features only if time allows

We should avoid spending too much time on advanced concepts before the core router works.

### Immediate priority

Implement **A*** pathfinding on the existing grid.

The first A* version should:

- Use the existing `get_neighbors()`
- Find a route from `start` to `goal`
- Avoid obstacles
- Use a suitable heuristic for the 4-direction grid
- Reconstruct the final path
- Display the path in Pygame

After that, we can add:

- Search visualization / animation
- Path cost
- Nodes explored
- Execution time
- Dijkstra comparison
- Traffic-aware costs
- Vehicle animation
- Dynamic replanning

---

## Planned Milestones

### Milestone 1 — Basic Grid ✅

- Pygame window
- 20×20 grid
- Mouse interaction
- Obstacles

### Milestone 2 — City Setup ✅ / In Progress

- Depot / Start
- Delivery / Goal
- Obstacles
- Neighbor detection

### Milestone 3 — A* Pathfinding ⏳

- Implement A*
- Manhattan heuristic
- Find valid route
- Reconstruct path
- Draw final route

### Milestone 4 — Visualization ⏳

- Show explored cells
- Animate search
- Animate final route

### Milestone 5 — Metrics ⏳

- Path cost
- Nodes explored
- Execution time
- Basic comparison data

### Milestone 6 — Dijkstra ⏳

- Implement Dijkstra
- Compare with A*
- Display differences

### Milestone 7 — Traffic / Weighted Routes ⏳

- Add traffic or movement costs
- Make route selection respond to different costs

### Milestone 8 — Vehicle Simulation ⏳

- Add delivery vehicle
- Move vehicle along calculated route

### Milestone 9 — Dynamic Replanning ⏳

- Change obstacles / traffic while route is active
- Recalculate route

### Milestone 10 — Final Working Prototype ⏳

- Combine the core features
- Improve UI
- Add project explanation / metrics
- Prepare a clean demonstration

---

## Target

**Short-term target:** Have a **decent working prototype** ready to demonstrate to the professor around **October 1st–8th**.

The prototype does not need to be fully refined at that point. The priority is to demonstrate that the main idea works:

> Create a city → place depot and delivery → add obstacles → run pathfinding → visualize a valid delivery route.

Further refinement and advanced logistics features can be added after the core working model is complete.

---

## Current File

`app.py`

## Run

```powershell
python app.py
```
