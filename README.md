# 🚚 AI-Powered Smart Logistics & Delivery Router

> **A map-based logistics routing system built in Python + Pygame,
> evolving from a basic A\* demonstration into a realistic
> road-constrained delivery router.**

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?logo=python)
![Algorithm](https://img.shields.io/badge/Algorithm-A*-purple)
![Map](https://img.shields.io/badge/Map-PUBG%20Livik-orange)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Project](https://img.shields.io/badge/Project-College%20DSA%20%2B%20AI%20Concepts-red)

------------------------------------------------------------------------

## 🌟 Project Overview

**AI-Powered Smart Logistics & Delivery Router** is a college project
focused on applying **Data Structures and Algorithms (DSA)** to a
visual, map-based logistics problem.

The project started as a simple grid-based A\* pathfinding
demonstration. The goal has now evolved into something much more
realistic:

``` text
Real-world-style map
        ↓
Map divided into a spatial grid
        ↓
Road network represented on the grid
        ↓
User selects start + destination
        ↓
A* searches only through road cells
        ↓
Search is animated visually
        ↓
Shortest road route is reconstructed
        ↓
Route is displayed on the map
        ↓
Future: vehicle simulation + traffic + replanning
```

The long-term vision is to simulate a small **smart logistics routing
system** rather than merely demonstrating A\* on an empty grid.

------------------------------------------------------------------------

# 🗺️ Current Project State

## Current milestone: **v0.6 --- Animated Road-Constrained A\***

The project currently uses a supplied **PUBG Livik map** as the visual
environment.

The map is represented using a:

-   **40 × 40 grid**
-   Approximate map size: **2 km × 2 km**
-   Approximate cell size: **50 m × 50 m**
-   Manually created road mask
-   **8-direction movement**
-   A\* pathfinding
-   Animated search
-   Animated final route

### Current visual behavior

The program displays:

  Visual            Meaning
  ----------------- -----------------------------
  🟥 Red cells      Currently marked road cells
  🔵 Blue cells     A\* open/frontier set
  🟣 Purple cells   A\* closed/explored set
  🟠 Orange cell    Current node being expanded
  🟡 Yellow route   Final shortest road route
  🔵 Blue marker    Start
  🔴 Red marker     Destination

> **Important:** The red-cell visualization is temporary. The current
> manually marked road cells make the underlying map roads harder to
> see. This is intentionally being left for a later improvement rather
> than delaying the routing work.

------------------------------------------------------------------------

# 🎯 Project Goals

The final project is intended to demonstrate several DSA and
intelligent-routing concepts in a visually understandable way.

### Core goals

-   [x] Build a grid-based environment
-   [x] Implement A\*
-   [x] Visualize A\* search
-   [x] Load a real map image
-   [x] Create a road-constrained grid
-   [x] Animate the search process
-   [ ] Add named map locations
-   [ ] Connect named locations to valid road cells
-   [ ] Improve road visualization
-   [ ] Add route metrics
-   [ ] Add a moving delivery vehicle
-   [ ] Add traffic/travel-time weighting
-   [ ] Add dynamic route replanning
-   [ ] Explore automatic road extraction from maps
-   [ ] Polish the final college demonstration

------------------------------------------------------------------------

# 🧠 DSA Concepts Used

The project is deliberately being built so that the algorithm is visible
rather than hidden behind a library.

## A\* Pathfinding

A\* evaluates candidate nodes using:

``` text
f(n) = g(n) + h(n)
```

Where:

-   `g(n)` = cost from the start to the current node
-   `h(n)` = estimated cost from the current node to the destination
-   `f(n)` = total estimated cost

The implementation uses a Python priority queue (`heapq`) to repeatedly
select the most promising node.

### Current movement model

The router supports 8-direction movement:

``` text
↖  ↑  ↗
←  •  →
↙  ↓  ↘
```

Movement costs are:

``` text
Straight movement = 1
Diagonal movement = √2
```

The heuristic is Euclidean distance, which matches the current
8-direction movement model.

------------------------------------------------------------------------

# 🛣️ Road-Constrained Routing

The important conceptual change from the original project is that **A\*
is no longer allowed to freely walk across the entire map**.

The map contains a manually constructed road mask.

Conceptually:

``` text
ROAD     → traversable
NON-ROAD → unavailable
```

The router therefore searches a **road graph embedded inside the map
grid**.

This gives the project a much more realistic structure:

``` text
Old:

Start ─────────────── Destination
       anywhere

Current:

Start → ROAD → ROAD → INTERSECTION
                         ↓
                       ROAD
                         ↓
                    Destination
```

------------------------------------------------------------------------

# 🎬 Animated Search

The search is intentionally animated.

Instead of:

``` text
Click
  ↓
Instant answer
```

the application shows:

``` text
Click
  ↓
A* begins
  ↓
Open/frontier nodes appear
  ↓
Nodes are explored
  ↓
Search progresses through the road network
  ↓
Destination reached
  ↓
Final route reconstructed
  ↓
Yellow route is animated
```

This is important for the college demonstration because it makes the
algorithm's behavior observable.

------------------------------------------------------------------------

# 🗺️ Map Representation

The current map is a supplied PUBG Livik map image:

``` text
PUBG_Mobile_Livik.jpg
```

The displayed map is scaled to an **800 × 800** Pygame window.

The current spatial model is:

``` text
40 rows × 40 columns
= 1600 cells
```

Approximate scale:

``` text
2 km / 40 cells
= 0.05 km per cell
= 50 metres per cell
```

This scale is currently being used as an approximate project model, not
as a precision geographic/GPS system.

------------------------------------------------------------------------

# 🧩 Current Architecture

The current prototype is intentionally simple.

``` text
app.py
│
├── Pygame initialization
│
├── Map loading
│
├── 40×40 road mask
│
├── Road-cell representation
│
├── 8-direction neighbour generation
│
├── A* initialization
│
├── Incremental A* search
│
├── Path reconstruction
│
├── Search animation
│
├── Route animation
│
└── UI / mouse interaction
```

The current implementation keeps the algorithm visible and
understandable rather than hiding everything inside classes or external
routing libraries.

------------------------------------------------------------------------

# 🖱️ Current Controls

### Left click

First click:

``` text
Select start
```

Second click:

``` text
Select destination
```

The A\* search then begins automatically.

### Right click

Resets the current route/search state.

------------------------------------------------------------------------

# 📊 Current Metrics

The prototype currently calculates an approximate route distance using:

``` text
number of movement units × 50 metres
```

Diagonal movement uses the corresponding `√2` movement cost.

More detailed metrics are planned for a later milestone.

------------------------------------------------------------------------

# 🚧 Known Limitations

This version is deliberately an intermediate milestone.

### 1. Road mask is manually created

The roads were manually marked on the 40×40 grid.

This was chosen because it lets us prove the routing architecture before
introducing computer vision.

### 2. Red road cells obscure the original map

The current visualization paints road cells red.

This makes the actual map roads harder to see with the naked eye.

**This is known and intentionally deferred.**

A future version should preserve the map's visual appearance while
showing the road network more elegantly.

### 3. 40×40 is relatively coarse

At approximately 50 m per cell, some intersections and narrow road
connections may not be represented perfectly.

8-direction movement helps connect nearby cells, but the grid can still
introduce:

-   small gaps
-   artificial diagonal connections
-   missed road branches
-   coarse intersections

The 40×40 version is being used first because it is manageable and
already provides a strong working demonstration.

### 4. Locations are currently grid-cell based

Named locations such as **Midstein** are not yet implemented.

The future design should avoid simply hardcoding a random grid cell as a
location.

Instead:

``` text
Named location
      ↓
Reference point / area
      ↓
Nearby valid road cells
      ↓
Connected road entry
      ↓
A* start / destination
```

### 5. No traffic model yet

The current route minimizes movement distance.

It does **not** yet calculate real travel time.

Traffic-aware routing is a future feature.

------------------------------------------------------------------------

# 🧭 Planned Development Roadmap

## v0.1 --- Basic Grid

Basic grid environment.

**Status: ✅ Complete**

------------------------------------------------------------------------

## v0.2 --- Depot + Destination

Added start/depot and destination concepts.

**Status: ✅ Complete**

------------------------------------------------------------------------

## v0.3 --- A\*

Implemented A\* pathfinding.

**Status: ✅ Complete**

------------------------------------------------------------------------

## v0.4 --- Animated A\*

Made the A\* search visually observable.

**Status: ✅ Complete**

------------------------------------------------------------------------

## v0.5 --- Real Map

Integrated the Livik map and moved away from a completely abstract grid.

**Status: ✅ Complete**

------------------------------------------------------------------------

## v0.6 --- Road-Constrained A\*

Created a manually marked road network and constrained A\* to road
cells.

Added animated search and route reconstruction.

**Status: ✅ Complete**

------------------------------------------------------------------------

## v0.7 --- Named Locations

Planned next.

Examples:

``` text
Midstein
Power Plant
East Port
Blomster
```

The exact available location list will be based on the map being used.

The important design principle is:

> A named location should resolve to a nearby valid connected road
> entry, not simply become an arbitrary grid coordinate.

**Status: ⏳ Next**

------------------------------------------------------------------------

## v0.8 --- Location-Based Map Routing

Move from:

``` text
Click road cell → Click road cell
```

toward:

``` text
Select named location → Select named location
```

Then resolve both locations onto the road network before running A\*.

**Status: ⏳ Planned**

------------------------------------------------------------------------

## v0.9 --- Route Metrics

Expand the information shown after routing:

-   approximate distance
-   number of explored nodes
-   number of route nodes
-   search duration
-   movement cost
-   potentially branching/intersection information

**Status: ⏳ Planned**

------------------------------------------------------------------------

## v1.0 --- Delivery Vehicle

A vehicle icon should follow the calculated route.

Conceptually:

``` text
A* route
   ↓
Route points
   ↓
Vehicle follows route
   ↓
Delivery reaches destination
```

**Status: ⏳ Planned**

------------------------------------------------------------------------

## v1.1 --- Traffic / Travel Time

Introduce weighted roads.

Instead of minimizing only:

``` text
distance
```

the router could eventually minimize:

``` text
estimated travel time
```

For example:

``` text
road cost =
distance × traffic factor
```

This creates the possibility of choosing:

``` text
Longer but faster road
```

instead of always choosing:

``` text
Shortest road
```

**Status: ⏳ Planned**

------------------------------------------------------------------------

## v1.2 --- Demonstration / UI Polish

Only after the core routing functionality is solid.

Possible additions:

-   clean legend
-   location selector
-   route information panel
-   better map overlays
-   vehicle information
-   improved animation controls
-   presentation-friendly layout

**Status: ⏳ Planned**

------------------------------------------------------------------------

## v1.3+ --- Advanced Features

Potential future work:

-   dynamic traffic changes
-   route replanning
-   blocked roads
-   temporary road closures
-   multiple delivery requests
-   multiple vehicles
-   delivery priorities
-   route optimization across multiple stops
-   D\* Lite / incremental replanning
-   automatic road extraction using computer vision

These should come **after** the core realistic router is stable.

------------------------------------------------------------------------

# 🌱 Why the Project Is Being Built Incrementally

The project is intentionally not jumping immediately into machine
learning, computer vision, or advanced pathfinding algorithms.

The development order is:

``` text
Understand A*
      ↓
Visualize A*
      ↓
Put A* on a real map
      ↓
Constrain A* to roads
      ↓
Add real locations
      ↓
Add vehicles
      ↓
Add traffic
      ↓
Add dynamic behaviour
      ↓
Add advanced intelligence
```

This makes each stage independently demonstrable and makes it easier to
explain the DSA concepts during evaluation.

------------------------------------------------------------------------

# 🛠️ Technology Stack

  Technology                Purpose
  ------------------------- ------------------------------------------
  **Python**                Main programming language
  **Pygame**                Interactive visualization and animation
  **heapq**                 Priority queue for A\*
  **A\***                   Core pathfinding algorithm
  **Grid representation**   Spatial map abstraction
  **Manual road mask**      Current road-network representation
  **PUBG Livik map**        Visual map environment
  **Git**                   Version control and milestone management

Pygame provides the display, event handling, image, drawing, timing, and
related functionality used by the interactive application. The official
documentation is available at https://www.pygame.org/docs/.

------------------------------------------------------------------------

# ▶️ Running the Project

Make sure Python and Pygame are installed.

Install Pygame if necessary:

``` bash
pip install pygame
```

Then run:

``` bash
python app.py
```

The project expects the map image to be available:

``` text
PUBG_Mobile_Livik.jpg
```

in the expected project location.

------------------------------------------------------------------------

# 🌿 Git Workflow

The project uses feature branches so that the stable `main` branch
remains recoverable.

Current development pattern:

``` text
main
 │
 ├── completed milestones
 │
 └── new feature branch
          ↓
       develop
          ↓
       test/demo
          ↓
       merge to main
```

### Current stable milestone

The animated road-constrained A\* milestone has been merged into:

``` text
main
```

The next major feature should be developed on a **new branch**.

Example:

``` bash
git switch -c named-locations
```

------------------------------------------------------------------------

# 📁 Important Files

At the current stage, the most important files are:

``` text
app.py
PUBG_Mobile_Livik.jpg
README.md
HANDOVER.md
```

`app.py` currently contains the main routing implementation and the
manually created road mask.

------------------------------------------------------------------------

# 🧪 Development Philosophy

This project prioritizes:

### 1. Correctness

The route should actually be generated by the algorithm.

### 2. Explainability

The DSA should be understandable during the demonstration.

### 3. Visual proof

The user should be able to see the search happening.

### 4. Incremental development

Every major milestone should run before moving to the next one.

### 5. Realistic evolution

The project should gradually move from an educational A\* demo toward a
believable logistics router.

------------------------------------------------------------------------

# 🏆 Current Achievement

At the current milestone, the project has moved from:

> **"A\* on a grid"**

to:

> **"A\* searching a manually constructed road network over a real map,
> with the search and final route animated."**

That is the current foundation for the rest of the logistics system.

------------------------------------------------------------------------

# 🔮 Final Vision

The eventual demonstration should feel like a small logistics routing
application:

``` text
┌─────────────────────────────────────────────┐
│       🚚 SMART LOGISTICS ROUTER             │
├─────────────────────────────────────────────┤
│                                             │
│          REAL MAP                            │
│                                             │
│      📍 Start                               │
│          │                                  │
│          └───────┐                          │
│                  └───────┐                  │
│                          🚚                │
│                            └───────📍       │
│                              Destination    │
│                                             │
├─────────────────────────────────────────────┤
│ Distance: ...   Time: ...   Nodes: ...      │
│ Traffic: ...   Status: Route found          │
└─────────────────────────────────────────────┘
```

The project is not there yet --- but the **core routing foundation is
now in place.** 🚚🗺️

------------------------------------------------------------------------

## 📌 Project Status

**Current version:** `v0.6`

**Current branch status:** Stable milestone merged into `main`

**Next major milestone:** `v0.7 — Named Locations`

**Current priority:** Keep the working router safe and build the next
feature on a separate branch.

------------------------------------------------------------------------

> \*\*Built as a college DSA project exploring A\*, spatial grids,
> road-constrained pathfinding, visualization, and intelligent logistics
> routing.\*\*
