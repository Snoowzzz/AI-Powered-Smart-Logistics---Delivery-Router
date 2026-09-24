# AI Smart Logistics Router — Progress Note

## Project Goal
Build a working **AI-Powered Smart Logistics & Delivery Router** in Pygame that can model a city grid, place a depot and delivery destination, handle obstacles, and eventually use pathfinding algorithms such as A* to find and visualize efficient delivery routes.

---

## Current Status

**Milestone 4 complete: Core A* pathfinding and animated search visualization are working.**

The basic Pygame grid is complete, and the application now has a working pathfinding pipeline:

- Depot / Start
- Delivery / Goal
- Obstacles / Blocked cells
- Valid neighboring cells
- A* pathfinding
- Manhattan heuristic
- Final path reconstruction
- Explored-cell visualization
- Step-by-step animated A* search

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
- A priority queue can be used to process the most promising A* cell next
- `g` represents the known cost from the start
- `h` represents an estimated remaining cost to the goal
- `f = g + h` combines the known and estimated costs
- Manhattan distance is appropriate for the current 4-direction movement
- `came_from` can reconstruct the final route
- A* can be separated into search state and visualization state
- The Pygame loop can advance the search one step at a time for animation

DSA knowledge should continue to be developed alongside the project rather than assuming advanced DSA knowledge.

---

## A* Pathfinding

### Core A* implementation

Implemented A* using:

- `heapq` as a priority queue
- `g_score` for the cost from the depot to a cell
- Manhattan distance as the heuristic
- `f = g + h` to prioritize cells
- `came_from` to remember the previous cell
- Path reconstruction once the delivery destination is reached

For the current 4-direction grid, each normal movement has a cost of `1`.

### Search visualization

A* now exposes the cells it has explored so the Pygame interface can visualize the algorithm.

- Blue cells = explored/search cells
- Yellow cells = final route
- Gray cells = obstacles
- Green cell = depot
- Red cell = delivery

### Animated search

The A* algorithm was changed from running completely in one function call to maintaining search state across the Pygame game loop.

The main search state includes:

- `open_heap`
- `came_from`
- `g_score`
- `explored`
- `searching`
- `search_finished`

`a_star_step()` performs one search step per game-loop iteration, allowing the explored area to appear progressively on screen.

This is an important architectural step because the pathfinding algorithm can now communicate its intermediate state to the visualization rather than only returning the final route.

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

The core A* router and search visualization are now working.

Next priorities:

- Add basic metrics
- Display path cost
- Display nodes explored
- Display execution time
- Then implement Dijkstra for comparison

After that, if time allows:

- Traffic-aware costs
- Vehicle animation
- Dynamic replanning
- UI refinement

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

### Milestone 3 — A* Pathfinding ✅

- Implement A*
- Manhattan heuristic
- Find valid route
- Reconstruct path
- Draw final route

### Milestone 4 — Visualization ✅

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
