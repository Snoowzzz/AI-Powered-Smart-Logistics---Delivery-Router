# AI-Powered Smart Logistics & Delivery Router

A Python and Pygame desktop application that demonstrates
road-constrained route planning with **A\***, vehicle-dependent road
costs, interactive road blocking, multi-stop delivery itineraries, route
analytics, and an **A\* versus Dijkstra** comparison.

> **Project scope:** This is an educational, map-based routing
> simulation built on a manually prepared grid and road masks. It is not
> a live navigation service and does not use live GPS, traffic, or
> delivery-time data.

## Contents

- [Overview](#overview)
- [Features](#features)
- [Technology](#technology)
- [Project files](#project-files)
- [Requirements](#requirements)
- [Setup and launch](#setup-and-launch)
- [How to use the application](#how-to-use-the-application)
- [How routing works](#how-routing-works)
- [Vehicle cost model](#vehicle-cost-model)
- [Route analytics](#route-analytics)
- [A\* versus Dijkstra](#a-versus-dijkstra)
- [No-route handling](#no-route-handling)
- [Testing checklist](#testing-checklist)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)

## Overview

The application uses a displayed Livik map image as the visual
background and represents the routable road network as an **80 × 80
grid**. Each grid cell represents approximately **25 metres**, using the
project's approximate 2 km × 2 km map scale.

Two text masks describe the road network:

- **Highway mask:** major roads with base multiplier `1.0`.
- **Weak-road mask:** secondary roads with a vehicle-specific
  multiplier.

The graph contains cells from either road mask. Named locations are
shown on the map, while manually selected road access cells in
`location_access_points.txt` define the actual routing endpoints. A\*
searches this graph and animates the search and final route.

## Features

- A\* search using a heap-based priority queue.
- Euclidean heuristic and eight-direction grid movement.
- Different movement costs for straight and diagonal steps.
- Highway and weak-road cost layers.
- Four vehicle profiles: Car, Bike, Truck, and Emergency.
- Animated search visualization and final route drawing.
- Route metrics: physical distance, highway distance, weak-road
  distance, weighted cost, and explored nodes.
- Interactive road blocking with pending selections, confirmation, and
  clear-all controls.
- Multi-stop itineraries with ordered intermediate stops and per-leg
  routing.
- A\* and Dijkstra comparison using the same active graph and vehicle
  weighting.
- Search-reduction percentage display.
- Connectivity check before animated A\* to identify unreachable
  endpoints early.
- Scrollable itinerary panel for long stop lists.
- Three-panel dashboard with route planner, map, route summary,
  vehicle controls, road blocking, route controls, and comparison
  card.

## Technology

- **Python 3**
- **Pygame** for the application window, rendering, controls, and
  animation
- Python standard library: `heapq`, `math`, `time`, and
  `collections.deque`

## Project files

Keep the following files together in the same application directory:

```text
project/
├── app.py     					 # Current application file 
├── PUBG_Mobile_Livik.jpg        # Map image loaded by the application
├── road_mask_80x80.txt          # Highway road mask
├── weak_road_mask_80x80.txt     # Weak-road mask
└── location_access_points.txt   # Named location to road-cell mapping
```

The exact filenames matter because the application loads them using
relative paths. The final submission folder should also include the
project report and this README. If your team uses `app_4.0.py` as the
canonical filename, rename the application file consistently and update
the launch command below.

### Road-mask format

Each mask must contain exactly **80 rows**, each with exactly **80
characters**. The only accepted characters are:

- `#` --- cell belongs to that road layer
- `.` --- cell does not belong to that road layer

### Access-point format

Each non-empty line uses this pattern:

```text
Location Name=row,column
```

Every configured location must have an entry, and its cell must belong
to the combined highway/weak-road network. The code validates these
conditions at startup.

## Requirements

- Python 3.10 or newer is a reasonable starting point; use the Python
  version already known to work on your project machine.
- Pygame installed in the same Python environment used to launch the
  app.
- The map image and all three routing-resource files listed above.

Install Pygame if needed:

```bash
python -m pip install pygame
```

On some systems, the launcher command is `python3` instead of `python`.

## Setup and launch

1. Put the application and required assets in one folder.
2. Open a terminal in that folder.
3. Confirm Python and Pygame are available:

   ```bash
   python --version
   python -m pip show pygame
   ```
4. Launch the app:

   ```bash
   python app.py
   ```
5. Confirm the window opens and the map, named locations, and all
   panels render.

Run the app from the project folder because the resource filenames are
relative paths.

## How to use the application

### Plan a single route

1. Click a named location on the map to select the start.
2. Click another named location to select the destination.
3. Watch the animated A\* search and final route.
4. Read the Route Summary panel and the A\* vs Dijkstra comparison
   card.

The application uses the named location's manually configured access
cell for routing, not simply the visual marker's pixel coordinate.

### Choose a vehicle

Select one of the four vehicle buttons before calculating a route. The
chosen profile affects the cost of entering weak-road cells. Vehicle
selection is disabled while a search or route animation is running.

### Block a road

1. Click **BLOCK ROAD**.
2. Click road cells on the map to add or remove pending blocks.
3. Click **CONFIRM BLOCKS** to apply pending selections.
4. Calculate a route and observe whether it detours around the blocked
   cells.
5. Use **CLEAR ALL BLOCKS** to restore the unblocked road graph.

The currently selected start and destination cells cannot be blocked. A
confirmed graph change resets the existing route state.

### Plan multiple delivery stops

1. Click **NEW MULTI-STOP PLAN**.
2. Select the start location.
3. Use **ADD STOP** and click intermediate locations in the order they
   should be visited.
4. Click **SET DESTINATION** and select the final location.
5. Click **CALCULATE ROUTE**.
6. Follow the itinerary on the left and review the accumulated route
   statistics.

`STOPS` counts intermediate stops only. It excludes the start and final
destination. Each leg is calculated between consecutive locations, and
the completed legs remain visible as the itinerary progresses.

## How routing works

### Grid and movement

The grid has 80 rows and 80 columns. A\* can move to any of the eight
neighboring cells if the cell belongs to the road network and is not
blocked.

- Horizontal/vertical movement: `1.0` grid unit.
- Diagonal movement: `sqrt(2)` grid units.

The implementation checks that a neighbor is inside the grid, is in the
combined road network, and is not in the confirmed blocked-cell set.

### A\* cost

A\* maintains:

- `open_heap`: priority queue ordered by estimated total cost.
- `g_score`: best known cost from the start to each cell.
- `came_from`: predecessor map used to reconstruct the route.
- `open_set` and `closed_set`: tracking sets for the search
  visualization and processing.

The priority is the accumulated cost plus heuristic estimate. The
heuristic is Euclidean distance in grid units. Because each edge costs
at least its geometric movement length and all road multipliers are at
least 1.0, this heuristic is admissible for the implemented cost model.

### Road connectivity

Before starting the animated search, the program runs a breadth-first
connectivity check using a queue. This check ignores weights because it
only determines whether a path exists. If the destination is
disconnected from the start under the current road blocks, the app
displays **NO ROUTE POSSIBLE** instead of animating a futile search. A\*
also has an open-heap exhaustion fallback.

## Vehicle cost model

Highway cells use multiplier `1.0` for every vehicle. Weak-road cells
use the selected profile:

  Vehicle       Weak-road multiplier

---

  Car                          1.50×
  Bike                         1.20×
  Truck                        2.20×
  Emergency              1.10×

For a move into a cell, the movement cost is the geometric step cost
multiplied by the multiplier for the road layer. Consequently, the route
with the lowest weighted cost is not necessarily the route with the
smallest physical distance.

If a cell appears in both masks, the current neighbor logic gives it the
highway multiplier because highway membership is checked first.

## Route analytics

The summary can report:

- **Distance:** physical path length converted to metres using the 25
  m cell scale.
- **Highway distance:** the part of the route traversing highway
  cells.
- **Weak-road distance:** the part traversing weak-road cells.
- **Weighted cost:** accumulated A\* graph cost in grid-cost units.
- **Explored nodes:** nodes processed by the search under the
  implementation's explored-node convention.
- **Stops:** intermediate delivery stops in a multi-stop itinerary.

The application uses `2 km / 80 cells = 25 m per cell` as its
approximate scale. Weighted cost is an algorithmic cost measure; it is
not a travel-time estimate.

For a multi-stop trip, the per-leg values are accumulated across the
itinerary. Explored-node totals across legs can count the same grid cell
more than once if it is explored on different legs.

## A\* versus Dijkstra

Dijkstra is used as a reference algorithm. Both searches use the same
`get_neighbors` function, so they share the current road masks, vehicle
multiplier, and confirmed blocked cells for the leg being compared.

The comparison displays:

- A\* explored nodes.
- Dijkstra explored nodes.
- Search reduction, calculated as:

  ```text
  (Dijkstra explored − A* explored)
  -------------------------------- × 100
          Dijkstra explored
  ```

  When Dijkstra's explored count is zero, the display uses `0%` to
  avoid division by zero.

For a reachable route, the key optimality check is that A\* and Dijkstra
produce the same **weighted cost** within a small floating-point
tolerance. Physical distance is reported separately and is not the
optimization objective, so physical route distances are not guaranteed
to match when multiple equal-cost routes exist.

A\* often explores fewer nodes because its heuristic directs the search
toward the goal, but this is an observed comparison, not a guarantee for
every possible route.

## No-route handling

A route can become impossible if confirmed blocks disconnect the start
from the destination. The app checks connectivity before animated A*. If
no route exists, it sets a no-route state and reports **NO ROUTE
POSSIBLE**. A* also detects failure if its open heap becomes empty.

To recover, clear some or all blocks or choose different endpoints.

## Testing checklist

Before submitting or demonstrating the project, perform a short final
acceptance pass:

- [ ] The app launches from the intended submission folder.
- [ ] The map image, both masks, and access-point file load.
- [ ] A short single route completes.
- [ ] A medium or long route animates and completes.
- [ ] All four vehicle profiles can be selected before routing.
- [ ] A weak-road route reflects the selected vehicle multiplier.
- [ ] A confirmed road block is avoided when an alternative exists.
- [ ] A disconnected route displays `NO ROUTE POSSIBLE`.
- [ ] A\* and Dijkstra weighted costs agree on a reachable route.
- [ ] Search-reduction percentage matches a manual calculation.
- [ ] A multi-stop route displays the correct stop count and
  accumulated totals.
- [ ] The itinerary remains readable with several stops.
- [ ] Clear All Blocks restores the original road graph behavior.
- [ ] README, report, screenshots, and submitted code describe the
  same version.

## Limitations

- The map scale and road masks are manually prepared approximations.
- There is no live GPS, live traffic, weather, real road database, or
  real delivery-time prediction.
- Vehicle profiles affect weak-road cost only; the model does not
  simulate vehicle dimensions, fuel, speed, or legal restrictions.
- Routes are limited to the road cells represented by the two masks.
- Multi-stop routing visits stops in the order chosen by the user; it
  does not optimize the stop order.
- Search-reduction values depend on the selected endpoints, vehicle,
  and road blocks.
- The map image is a visual backdrop; the route graph comes from the
  text masks and access-point mapping.

## Troubleshooting

**The app cannot find an image or text file.**
Run the command from the project directory and verify all required
assets are alongside the Python file.

**A mask fails validation.**
Check that it has 80 lines, each 80 characters long, using only `#` and
`.`.

**An access point fails validation.**
Confirm every location name matches the code's location dictionary
exactly, coordinates are integers in `row,column` order, and the cell
belongs to one of the road masks.

**A route is impossible.**
Clear road blocks and try again. If it remains impossible, inspect
connectivity in the combined road masks and access-point coordinates.

**The wrong Python environment is used.**
Install Pygame using the same interpreter that launches the app, for
example `python -m pip install pygame`.

---

## Project completion note

This project demonstrates practical use of graph search, priority
queues, heuristic search, weighted edges, path reconstruction, graph
modification, multi-leg planning, and algorithm comparison in an
interactive desktop application.
