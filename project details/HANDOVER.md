# 🔄 AI-Powered Smart Logistics & Delivery Router --- Handover

> **Purpose:** This file is a continuity document for the next
> development session. Read this before making project changes.

------------------------------------------------------------------------

# 1. PROJECT IDENTITY

Project name:

**AI-Powered Smart Logistics & Delivery Router**

Language:

**Python**

Visualization:

**Pygame**

Core algorithm:

**A\***

Current map:

**PUBG Livik map**

Current stable milestone:

**v0.6 --- Animated Road-Constrained A\***

------------------------------------------------------------------------

# 2. CURRENT STATUS --- VERY IMPORTANT

The project has successfully moved beyond a basic A\* grid
demonstration.

The current application:

1.  Loads the Livik map image.
2.  Displays it in an 800×800 Pygame window.
3.  Uses a 40×40 spatial grid.
4.  Contains a manually created road mask.
5.  Treats marked cells as road/traversable cells.
6.  Uses 8-direction movement.
7.  Runs A\* only through the road network.
8.  Animates the A\* search.
9.  Shows open/frontier cells.
10. Shows explored/closed cells.
11. Shows the current node.
12. Reconstructs the final path.
13. Animates the final route in yellow.
14. Calculates an approximate route distance.

The user tested it and explicitly liked the result, especially:

-   the way the route/search lines flow
-   the animated search
-   the overall visual effect

This milestone has been merged into `main`.

------------------------------------------------------------------------

# 3. USER'S CURRENT ASSESSMENT

The user considers this a **major successful milestone**.

They specifically liked:

> "the lines ... go well extremely nicely"

and:

> "i like the animation too"

The user is happy with the current result.

Do not immediately redesign the animation or replace the current
algorithm.

------------------------------------------------------------------------

# 4. KNOWN VISUAL ISSUE

The biggest current visual issue is the road visualization.

The manually marked road cells are displayed as red blocks.

Because of this:

> the actual roads on the underlying map are difficult to see with the
> naked eye.

The user explicitly said:

> "the red block thing we will deal with later on"

Therefore:

## DO NOT make this the next task automatically.

The red overlay is currently acceptable as a proof-of-concept.

The later solution should make the road network visible without covering
the map so heavily.

Possible future direction:

``` text
Current:
Map + solid red road cells

Future:
Map + subtle road overlay / highlighted road centerline / cleaner mask
```

But do not implement this unless it becomes the agreed next task.

------------------------------------------------------------------------

# 5. CURRENT GRID MODEL

Current grid:

``` text
ROWS = 40
COLS = 40
```

Total cells:

``` text
40 × 40 = 1600
```

Map approximation:

``` text
2 km × 2 km
```

Cell scale:

``` text
2.0 km / 40
= 0.05 km
= 50 m
```

So the current approximate model is:

``` text
1 cell ≈ 50 metres
```

This is a project approximation, not a precision GIS coordinate system.

------------------------------------------------------------------------

# 6. ROAD MASK

The current road network is manually encoded inside `app.py` as a
40×40-ish collection of strings using:

``` text
#
.
```

Interpretation:

``` text
# = ROAD / traversable
. = NON-ROAD / unavailable
```

Important terminology issue:

The original marking UI called the marked cells **"Blocked"**, but for
the current routing experiment the marked/red cells are being
interpreted as **ROAD** cells.

Do not accidentally invert this logic.

The road mask took significant manual effort.

The user does not want to redo it casually.

If modifying the grid resolution, preserve the existing mask or create a
migration strategy rather than throwing it away.

------------------------------------------------------------------------

# 7. MOVEMENT MODEL

A\* currently supports 8-direction movement:

``` text
↖ ↑ ↗
← • →
↙ ↓ ↘
```

Costs:

``` text
horizontal/vertical = 1
diagonal = sqrt(2)
```

The heuristic is Euclidean distance.

This is appropriate for the current movement model.

------------------------------------------------------------------------

# 8. A\* IMPLEMENTATION

The current search is incremental/stateful rather than one-shot.

The implementation uses:

``` python
heapq
```

for the priority queue.

Important structures include:

``` text
open_heap
came_from
g_score
closed_set
open_set
```

The search advances one expansion at a time with a delay.

The implementation also handles **stale heap entries** by storing enough
information in the heap entry to verify that the popped entry still
represents the current best `g` value.

Do not remove that stale-entry handling.

------------------------------------------------------------------------

# 9. CURRENT ANIMATION

Current approximate timing:

``` text
SEARCH_DELAY = 0.08
PATH_DELAY = 0.05
```

Meaning:

-   A\* expansion is visible progressively.
-   After search completes, the final path is drawn progressively.

The current animation has been positively reviewed by the user.

Avoid changing timing unless the user asks or testing shows a problem.

------------------------------------------------------------------------

# 10. CURRENT VISUAL STATES

Current visual meaning:

``` text
RED      = manually marked road cells
BLUE     = A* open/frontier set
PURPLE   = A* closed/explored set
ORANGE   = current node
YELLOW   = final route
BLUE     = start marker
RED      = destination marker
```

There is an unavoidable visual overlap between road red and destination
red. This can be improved later.

------------------------------------------------------------------------

# 11. CURRENT USER CONTROLS

Left click:

``` text
First click  → start
Second click → destination
```

Then A\* begins.

Right click:

``` text
reset
```

The current interface selects road cells directly.

------------------------------------------------------------------------

# 12. CURRENT ROUTING MODEL

The current routing objective is:

> **Shortest road distance / movement cost**

It is NOT yet:

> fastest travel time

There is currently no traffic weighting.

Future traffic routing can introduce weighted travel-time costs.

Example future concept:

``` text
travel_cost = distance × traffic_factor
```

But do not implement this before named locations and the basic route
flow are stable.

------------------------------------------------------------------------

# 13. IMPORTANT LOCATION DESIGN

The next major milestone is:

## v0.7 --- Named Locations

Examples might include map locations such as:

``` text
Midstein
Power Plant
East Port
Blomster
```

The exact location list must match the supplied map and should be
verified before implementation.

### Critical design rule

Do NOT simply do:

``` text
Midstein = arbitrary grid cell
```

Instead:

``` text
Named location
       ↓
reference point / area
       ↓
nearby valid road cells
       ↓
connected road entry
       ↓
A* start node
```

And the same process for the destination.

This is important because a named place is an area/reference point,
while A\* needs a valid traversable road node.

------------------------------------------------------------------------

# 14. EXPECTED NEXT USER-FACING FLOW

Eventually the current:

``` text
click road cell
click road cell
```

interaction should become something like:

``` text
Select start location
        ↓
Select destination
        ↓
Resolve both to nearby connected road nodes
        ↓
Run animated A*
        ↓
Show route
        ↓
Show metrics
```

The map should remain visible throughout.

------------------------------------------------------------------------

# 15. DEVELOPMENT ROADMAP

Current roadmap:

``` text
v0.1 Basic grid                  ✅
v0.2 Depot/destination           ✅
v0.3 A*                          ✅
v0.4 Animated A*                 ✅
v0.5 Real map + finer grid      ✅
v0.6 Road-constrained A*        ✅ CURRENT
v0.7 Named locations             ⏳ NEXT
v0.8 Map-based location routing  ⏳
v0.9 Route metrics               ⏳
v1.0 Vehicle animation           ⏳
v1.1 Traffic/travel time         ⏳
v1.2 UI/demo polish              ⏳
v1.3+ Replanning/advanced        ⏳
```

Potential advanced work later:

-   dynamic traffic
-   blocked roads
-   road closures
-   vehicle simulation
-   multiple delivery requests
-   multiple vehicles
-   multi-stop optimization
-   dynamic replanning
-   D\* Lite
-   automatic road detection / computer vision

Do not jump to these prematurely.

------------------------------------------------------------------------

# 16. PROJECT DEVELOPMENT PHILOSOPHY

The user is comfortable with Python but is still learning DSA concepts.

When teaching a new concept:

-   explain it briefly
-   explain why it is needed
-   then show the complete implementation

The user strongly prefers:

> **Complete replacement code in one block**

rather than many fragmented edits.

For each major milestone:

1.  Explain what we are building.
2.  Explain the new DSA concept if necessary.
3.  Give complete code.
4.  Give exact placement/instructions.
5.  Make it runnable.
6.  Test/demo it.
7.  Commit it.
8.  Merge stable milestones into `main`.
9.  Start the next feature on a new branch.

------------------------------------------------------------------------

# 17. GIT WORKFLOW

Current stable branch:

``` text
main
```

The completed realistic routing branch was:

``` text
realistic-map-router
```

That work has now been merged into `main`.

The user explicitly wants future major features developed on separate
branches.

Recommended next branch:

``` bash
git switch -c named-locations
```

Do not develop experimental major features directly on `main`.

After a milestone is stable:

``` bash
git add .
git commit -m "..."
git switch main
git merge named-locations
```

Then create the next feature branch.

------------------------------------------------------------------------

# 18. IMPORTANT FILES

Current important files:

``` text
app.py
PUBG_Mobile_Livik.jpg
README.md
HANDOVER.md
```

The current routing implementation is primarily inside:

``` text
app.py
```

The road mask is also currently inside `app.py`.

Before making architectural changes, inspect the actual current `app.py`
rather than reconstructing it from memory.

------------------------------------------------------------------------

# 19. DO NOT ASSUME THE ROAD MASK

There was a manually created 40×40 road mask during development.

It was entered as strings containing `#` and `.`.

However, some manually transcribed representations may be visually
confusing about exact string lengths.

Therefore:

> **Use the actual `app.py` in the project as the source of truth.**

Do not paste an old remembered road mask over the working version unless
explicitly required.

------------------------------------------------------------------------

# 20. CURRENT TECHNICAL BASELINE

The current program roughly follows this structure:

``` text
Pygame setup
      ↓
Load Livik image
      ↓
Scale image to 800×800
      ↓
40×40 road mask
      ↓
Build road_cells
      ↓
Mouse selects start/goal
      ↓
Initialize A*
      ↓
Incremental heap-based search
      ↓
Draw open/closed/current states
      ↓
Goal reached
      ↓
Reconstruct path
      ↓
Animate yellow route
      ↓
Show route distance
```

This is the baseline that should be preserved.

------------------------------------------------------------------------

# 21. WHAT THE PROFESSOR WANTED

The professor previously considered the basic grid/A\* implementation
technically correct but too much like:

> "ticking a box"

That feedback caused the project direction to change.

The response was to move toward:

``` text
real map
+
roads
+
locations
+
animated search
+
logistics behaviour
```

The current project is therefore specifically trying to demonstrate
**application of DSA to a realistic logistics problem**, rather than
just proving that A\* can find a path.

------------------------------------------------------------------------

# 22. WHY 40×40 WAS CHOSEN

The user manually created the current road mask at 40×40.

It took substantial effort.

The current plan is to test whether 40×40 is sufficient before
increasing resolution.

The user specifically wants to avoid redoing the road marking
unnecessarily.

Potential future issue:

``` text
Two road cells may look connected visually
but be disconnected in the discrete grid.
```

8-direction movement helps with this, but it does not eliminate all
coarse-grid problems.

------------------------------------------------------------------------

# 23. AUTOMATIC ROAD DETECTION --- FUTURE ONLY

A future idea is to automatically detect roads from arbitrary map images
using image processing / computer vision.

This is interesting but is NOT the current task.

Current priority:

``` text
manual road network
→ named locations
→ reliable routing
→ vehicle
→ traffic
→ then automatic road detection
```

Do not replace the working manual mask with computer vision prematurely.

------------------------------------------------------------------------

# 24. NEXT SESSION --- RECOMMENDED START

When the next chat begins, first establish:

``` text
Current version = v0.6
main is stable
animated road-constrained A* works
red road blocks are known but intentionally deferred
next milestone = v0.7 Named Locations
```

Then inspect the actual current `app.py`.

The first design question should be:

> How should named Livik locations map to nearby connected road cells?

A good first implementation should likely introduce a location data
structure containing:

``` text
name
reference row/column or screen position
optional radius/area
```

Then calculate/select nearby road cells.

Avoid making the location itself a route node if it is not on a road.

------------------------------------------------------------------------

# 25. CURRENT SUCCESS CRITERIA

The current milestone is considered successful because:

-   the map is real
-   roads constrain the search
-   A\* visibly explores the network
-   the search is animated
-   the final route is animated
-   the result is visually understandable
-   the user is satisfied with the behavior

Do not break these qualities while implementing the next feature.

------------------------------------------------------------------------

# 26. SHORT VERSION

If only a few seconds are available to understand the project:

``` text
PROJECT:
AI-Powered Smart Logistics & Delivery Router

LANGUAGE:
Python

UI:
Pygame

CURRENT VERSION:
v0.6

CURRENT STATE:
Real Livik map + 40×40 manually marked road network +
8-direction A* + animated search + animated final route.

ROAD:
# means traversable road in the current mask.
The old marking UI called these cells "Blocked", but that
terminology is misleading for the current implementation.

KNOWN ISSUE:
Red road-cell overlays hide the actual map roads.
User explicitly wants this fixed later, not now.

NEXT:
v0.7 Named Locations.

IMPORTANT:
Named locations must resolve to nearby valid connected road
cells instead of being arbitrary A* nodes.

GIT:
Current stable version is merged into main.
Future major work should use a new feature branch.

USER PREFERENCE:
Complete code blocks, exact placement instructions,
short DSA explanations, runnable milestones.

DO NOT:
Jump to computer vision, D* Lite, ML, or traffic before
the named-location routing foundation is stable.
```

------------------------------------------------------------------------

# 27. HANDOVER PRINCIPLE

This document is intentionally written as a **continuity snapshot**, not
as a replacement for the source code.

If anything in this document conflicts with the actual current code:

> **The actual project files are the source of truth.**

Always inspect the current implementation before making a significant
change.

------------------------------------------------------------------------

**End of handover --- current project checkpoint: v0.6** 🚚🗺️
