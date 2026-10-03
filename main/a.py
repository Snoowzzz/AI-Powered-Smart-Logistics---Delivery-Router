import pygame
import heapq
import math
import time

pygame.init()

# ============================================================
# AI SMART LOGISTICS ROUTER
# v0.8.6 - 80x80 Route Analytics + Vehicle Profiles
#
# Highway and weak-road masks are used for routing, but the
# road cells themselves are NOT drawn on the map.
#
# Search visualization:
#   Blue   = open set
#   Purple = closed set
#   Orange = current A* node
#   Yellow = final route LINE (not blocks)
# ============================================================

WIDTH = 800
HEIGHT = 800

# Layout:
#   Left panel  = Route Details
#   Center      = unchanged 800x800 map
#   Right panel = road blocking + multi-stop controls
LEFT_PANEL_WIDTH = 360
RIGHT_PANEL_WIDTH = 360
MAP_X = LEFT_PANEL_WIDTH
RIGHT_PANEL_X = MAP_X + WIDTH
WINDOW_WIDTH = LEFT_PANEL_WIDTH + WIDTH + RIGHT_PANEL_WIDTH

# The map remains exactly 800x800. The extra window space is used
# only for the Route Details panel, so map/grid coordinates do not change.
screen = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router - v0.8.7")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 15)
popup_title_font = pygame.font.SysFont("Arial", 22, bold=True)
popup_font = pygame.font.SysFont("Arial", 17)
popup_small_font = pygame.font.SysFont("Arial", 14)
right_section_font = pygame.font.SysFont("Arial", 15, bold=True)
right_hint_font = pygame.font.SysFont("Arial", 13)
section_font = pygame.font.SysFont("Arial", 15, bold=True)
metric_font = pygame.font.SysFont("Arial", 18, bold=True)
accent_font = pygame.font.SysFont("Arial", 16, bold=True)
comparison_font = pygame.font.SysFont("Arial", 13, bold=True)

# Route-information popup. It is drawn over the map rather than
# opening a separate operating-system window, so the application
# remains self-contained and the A* animation stays visible behind it.
POPUP_WIDTH = 340
POPUP_HEIGHT = 455
POPUP_X = 10
POPUP_Y = 18

# The popup can be moved by dragging its header. These values are
# deliberately kept as separate state so the popup can be repositioned
# without affecting the map or routing logic.
popup_dragging = False
popup_drag_offset_x = 0
popup_drag_offset_y = 0
popup_route_scroll = 0

# ============================================================
# INTERACTIVE ROAD BLOCKING — STAGE 3
# ============================================================
# Users can select multiple road cells, review them, and then
# confirm the blocks. Confirmed blocks are excluded by A*.
blocked_cells = set()
pending_block_cells = set()
block_mode = False
block_button_rect = pygame.Rect(RIGHT_PANEL_X + 20, 273, 150, 38)
confirm_blocks_rect = pygame.Rect(RIGHT_PANEL_X + 185, 273, 155, 38)
clear_blocks_rect = pygame.Rect(RIGHT_PANEL_X + 20, 320, 320, 36)

# ============================================================
# MULTI-STOP ROUTING — STAGE 3 EXTENSION
# ============================================================
# The user can build a route plan such as:
# Start -> Stop 1 -> Stop 2 -> ... -> Destination
# Each leg reuses the existing A* engine.
multi_stop_mode = False
multi_selection_phase = "start"  # start, stops, destination, ready
multi_route_points = []
multi_leg_index = 0
multi_leg_paths = []
multi_leg_stats = []
multi_total_distance_m = 0.0
multi_total_highway_m = 0.0
multi_total_weak_m = 0.0
multi_total_weighted_cost = 0.0
multi_total_explored = 0
multi_pending_next_leg = False

multi_route_button_rect = pygame.Rect(RIGHT_PANEL_X + 20, 492, 320, 40)
multi_add_stop_rect = pygame.Rect(RIGHT_PANEL_X + 20, 540, 155, 40)
multi_set_destination_rect = pygame.Rect(RIGHT_PANEL_X + 185, 540, 155, 40)
multi_calculate_rect = pygame.Rect(RIGHT_PANEL_X + 20, 590, 320, 42)

# ============================================================
# VEHICLE PROFILES — STAGE 2
# ============================================================
# Highway remains 1.00 for every vehicle.
# Vehicle-specific weak-road multipliers.
# Highway remains 1.00 for every vehicle.
VEHICLE_PROFILES = {
    "Car": 1.50,
    "Bike": 1.20,
    "Truck": 2.20,
    "Emergency": 1.10,
}

selected_vehicle = "Car"
vehicle_button_rects = {}

def get_selected_vehicle_multiplier():
    return VEHICLE_PROFILES[selected_vehicle]

def set_vehicle(vehicle_name):
    global selected_vehicle
    if vehicle_name in VEHICLE_PROFILES and not searching and not path_animation:
        selected_vehicle = vehicle_name

def get_vehicle_button_rects():
    # Four buttons in a 2x2 grid in the dedicated right panel.
    names = list(VEHICLE_PROFILES.keys())
    rects = {}

    left = RIGHT_PANEL_X + 20
    top = 62
    gap = 10
    button_width = 155
    button_height = 38

    for index, name in enumerate(names):
        row = index // 2
        col = index % 2
        rects[name] = pygame.Rect(
            left + col * (button_width + gap),
            top + row * (button_height + gap),
            button_width,
            button_height
        )

    return rects

def get_popup_rect():
    return pygame.Rect(POPUP_X, POPUP_Y, POPUP_WIDTH, POPUP_HEIGHT)

def get_popup_close_rect():
    return pygame.Rect(
        POPUP_X + POPUP_WIDTH - 38,
        POPUP_Y + 10,
        26,
        26
    )

def get_popup_header_rect():
    # The header/title area is the drag handle.
    return pygame.Rect(
        POPUP_X,
        POPUP_Y,
        POPUP_WIDTH,
        48
    )

def clamp_popup_position(x, y):
    # Route Details can move only inside the dedicated left panel.
    x = max(
        10,
        min(x, LEFT_PANEL_WIDTH - POPUP_WIDTH - 10)
    )
    y = max(
        0,
        min(y, HEIGHT - POPUP_HEIGHT)
    )
    return x, y

# ============================================================
# MAP
# ============================================================

map_image = pygame.image.load("PUBG_Mobile_Livik.jpg")

MAP_ORIGINAL_WIDTH, MAP_ORIGINAL_HEIGHT = map_image.get_size()

map_image = pygame.transform.scale(
    map_image,
    (WIDTH, HEIGHT)
)

# ============================================================
# GRID
# ============================================================

ROWS = 80
COLS = 80

CELL_SIZE = WIDTH // COLS

# ============================================================
# REAL WORLD SCALE
# ============================================================

MAP_SIZE_KM = 2.0
CELL_SIZE_KM = MAP_SIZE_KM / COLS

# ============================================================
# ROAD MASK FILES
# ============================================================

HIGHWAY_MASK_FILE = "road_mask_80x80.txt"
WEAK_MASK_FILE = "weak_road_mask_80x80.txt"
ACCESS_POINTS_FILE = "location_access_points.txt"

def load_mask(filename):
    """Load an 80x80 '#' / '.' road mask."""

    with open(filename, "r", encoding="utf-8") as file:
        rows = [line.rstrip("\n\r") for line in file]

    if len(rows) != ROWS:
        raise ValueError(
            f"{filename} must contain {ROWS} rows."
        )

    if any(len(row) != COLS for row in rows):
        raise ValueError(
            f"Every row in {filename} must contain {COLS} characters."
        )

    if any(
        character not in ".#"
        for row in rows
        for character in row
    ):
        raise ValueError(
            f"{filename} may contain only '.' and '#'."
        )

    return {
        (row, col)
        for row in range(ROWS)
        for col in range(COLS)
        if rows[row][col] == "#"
    }


# Load both road layers.
highway_cells = load_mask(HIGHWAY_MASK_FILE)
weak_cells = load_mask(WEAK_MASK_FILE)

# A* can travel on either road type.
road_cells = highway_cells | weak_cells


# ============================================================
# LOCATION ACCESS POINTS
# ============================================================

# Each named location has one exact 80x80 road cell selected
# manually with the location-access marker tool.

def load_access_points(filename):
    """Load named-location access cells from name=row,col lines."""

    access_points = {}

    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):

            line = line.strip()

            if not line:
                continue

            if "=" not in line:
                raise ValueError(
                    f"Invalid access-point entry on line {line_number}: {line}"
                )

            name, coordinates = line.split("=", 1)
            name = name.strip()

            if name not in LOCATION_POINTS:
                raise ValueError(
                    f"Unknown location in access-point file: {name}"
                )

            try:
                row_text, col_text = coordinates.split(",", 1)
                row = int(row_text.strip())
                col = int(col_text.strip())
            except ValueError:
                raise ValueError(
                    f"Invalid coordinates for {name}: {coordinates}"
                )

            cell = (row, col)

            if cell not in road_cells:
                raise ValueError(
                    f"Access point for {name} {cell} is not a road cell."
                )

            access_points[name] = cell

    missing = set(LOCATION_POINTS) - set(access_points)

    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(
            "Missing access points for: " + missing_text
        )

    return access_points

# ============================================================
# NAMED LOCATIONS
# ============================================================
#
# These are reference points on the original Livik image.
# They are NOT A* nodes.
#
# Each location also has an exact road access cell stored in
# location_access_points.txt. The reference point is used only
# for the clickable visual marker.
# ============================================================

LOCATION_POINTS = {
    "Wengen": (109.8, 79.6),
    "Gass": (276.2, 79.6),
    "Rose Farm": (429.5, 44.6),
    "Iceborg": (594.2, 119.9),
    "Lupin Felt": (133.3, 133.9),
    "Hot Spring": (470.5, 180.3),
    "Blomster": (135.0, 225.8),
    "Gronhus": (299.7, 224.9),
    "Crabgrass": (199.5, 327.3),
    "East Port": (619.5, 329.9),
    "Midstein": (430.4, 379.8),
    "Fisherhus": (571.5, 405.1),
    "Aqueduct": (140.3, 449.8),
    "Reeds": (403.4, 460.3),
    "Helle": (29.6, 499.6),
    "Power Plant": (236.1, 490.0),
    "Waterfall": (569.8, 530.3),
    "Shipyard": (673.5, 539.9),
    "Holdhus": (89.7, 600.3),
    "Askehus": (260.5, 639.6),
    "Lumber Yard": (500.1, 620.4),
}

LOCATION_RADIUS = 24

LOCATION_ACCESS = load_access_points(ACCESS_POINTS_FILE)


def location_to_screen(point):
    """Convert original-map pixels to displayed-map pixels."""

    x, y = point

    screen_x = MAP_X + int(
        x * WIDTH / MAP_ORIGINAL_WIDTH
    )

    screen_y = int(
        y * HEIGHT / MAP_ORIGINAL_HEIGHT
    )

    return screen_x, screen_y


def screen_to_cell(position):
    """Convert displayed-map pixels to an 80x80 cell."""

    x, y = position

    # Convert screen coordinates back to map-local coordinates.
    x -= MAP_X

    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)

    if 0 <= row < ROWS and 0 <= col < COLS:
        return row, col

    return None


def find_clicked_location(mouse_position):
    """Return a nearby named location, if one was clicked."""

    mouse_x, mouse_y = mouse_position

    best_name = None
    best_distance = float("inf")

    for name, point in LOCATION_POINTS.items():

        location_x, location_y = location_to_screen(point)

        distance = math.sqrt(
            (mouse_x - location_x) ** 2
            +
            (mouse_y - location_y) ** 2
        )

        if (
            distance <= LOCATION_RADIUS
            and
            distance < best_distance
        ):
            best_name = name
            best_distance = distance

    return best_name


# ============================================================
# A* MOVEMENT
# ============================================================

directions = [
    (-1, -1),
    (-1,  0),
    (-1,  1),

    ( 0, -1),
    ( 0,  1),

    ( 1, -1),
    ( 1,  0),
    ( 1,  1),
]


def get_neighbors(cell):

    row, col = cell

    neighbors = []

    for dr, dc in directions:

        new_row = row + dr
        new_col = col + dc

        if not (
            0 <= new_row < ROWS
            and
            0 <= new_col < COLS
        ):
            continue

        new_cell = (new_row, new_col)

        # Stage 3: blocked road cells are removed from the graph
        # for the current routing run.
        if new_cell in blocked_cells:
            continue

        if new_cell not in road_cells:
            continue

        if dr == 0 or dc == 0:
            geometric_cost = 1.0
        else:
            geometric_cost = math.sqrt(2)

        if new_cell in highway_cells:
            road_multiplier = 1.0
        elif new_cell in weak_cells:
            road_multiplier = get_selected_vehicle_multiplier()
        else:
            continue

        cost = geometric_cost * road_multiplier

        neighbors.append(
            (new_cell, cost)
        )

    return neighbors


# ============================================================
# HEURISTIC
# ============================================================

def heuristic(a, b):

    row1, col1 = a
    row2, col2 = b

    return math.sqrt(
        (row2 - row1) ** 2
        +
        (col2 - col1) ** 2
    )


# ============================================================
# DIJKSTRA REFERENCE SEARCH
# ============================================================

def dijkstra_search(start_cell, goal_cell):
    """Run Dijkstra on the exact same weighted graph as A*."""

    distance = {start_cell: 0.0}
    came_from_dijkstra = {}
    explored = set()

    heap = [(0.0, start_cell)]

    while heap:
        current_cost, current_node = heapq.heappop(heap)

        # Ignore stale priority-queue entries.
        if current_cost != distance.get(
            current_node,
            float("inf")
        ):
            continue

        # Keep the same explored-node convention as A*: the goal is
        # reached before it is added to A*'s closed_set.
        if current_node == goal_cell:
            path = [current_node]
            node = current_node

            while node in came_from_dijkstra:
                node = came_from_dijkstra[node]
                path.append(node)

            path.reverse()

            return path, current_cost, explored

        explored.add(current_node)

        for neighbor, movement_cost in get_neighbors(current_node):
            new_cost = current_cost + movement_cost

            if new_cost < distance.get(
                neighbor,
                float("inf")
            ):
                distance[neighbor] = new_cost
                came_from_dijkstra[neighbor] = current_node

                heapq.heappush(
                    heap,
                    (new_cost, neighbor)
                )

    return [], float("inf"), explored


def calculate_dijkstra_statistics(path, weighted_cost):
    """Calculate the same physical route metrics used by A*."""

    route = 0.0
    highway = 0.0
    weak = 0.0

    for i in range(1, len(path)):
        a = path[i - 1]
        b = path[i]

        dr = abs(b[0] - a[0])
        dc = abs(b[1] - a[1])
        movement = math.sqrt(2) if dr == 1 and dc == 1 else 1.0

        route += movement

        if b in highway_cells:
            highway += movement
        elif b in weak_cells:
            weak += movement

    return (
        route * CELL_SIZE_KM * 1000,
        highway * CELL_SIZE_KM * 1000,
        weak * CELL_SIZE_KM * 1000,
        weighted_cost
    )


def compare_astar_vs_dijkstra():
    """Compare Dijkstra with the A* route just calculated."""

    global dijkstra_distance_m
    global dijkstra_highway_distance_m
    global dijkstra_weak_distance_m
    global dijkstra_weighted_cost
    global dijkstra_explored_nodes
    global comparison_available
    global comparison_cost_matches
    global comparison_distance_matches

    if start is None or goal is None:
        return

    path, cost, explored = dijkstra_search(
        start,
        goal
    )

    dijkstra_explored_nodes = len(explored)
    comparison_available = True

    if not path:
        dijkstra_distance_m = 0.0
        dijkstra_highway_distance_m = 0.0
        dijkstra_weak_distance_m = 0.0
        dijkstra_weighted_cost = float("inf")
        comparison_cost_matches = False
        comparison_distance_matches = False
        return

    (
        dijkstra_distance_m,
        dijkstra_highway_distance_m,
        dijkstra_weak_distance_m,
        dijkstra_weighted_cost
    ) = calculate_dijkstra_statistics(
        path,
        cost
    )

    comparison_cost_matches = math.isclose(
        weighted_route_cost,
        dijkstra_weighted_cost,
        rel_tol=1e-9,
        abs_tol=1e-9
    )

    # Physical distance is reported for both algorithms, but it is
    # not used as the correctness criterion because the router
    # optimizes weighted cost, not raw distance.
    comparison_distance_matches = math.isclose(
        route_distance_m,
        dijkstra_distance_m,
        rel_tol=1e-9,
        abs_tol=1e-9
    )


# ============================================================
# WEIGHTED COST UNITS / A* OPTIMALITY
# ============================================================
# Straight move = 1.0 grid-cell unit.
# Diagonal move = sqrt(2) grid-cell units.
# Highway multiplier = 1.0.
# Weak-road multipliers are >= 1.1.
#
# Euclidean distance is therefore an admissible/consistent heuristic:
# every allowed edge costs at least its Euclidean geometric length.
# The map scale is 2 km / 80 cells = 25 m/cell. Multiplying a
# weighted cell cost by 25 m is only a unit conversion and does not
# change which route minimizes the weighted objective.
# ============================================================

# ============================================================
# A* STATE
# ============================================================

open_heap = []
came_from = {}
g_score = {}

start = None
goal = None
current = None

closed_set = set()
open_set = set()

final_path = []
path_index = 0

searching = False
path_animation = False
finished = False

# Route popup state. The popup appears as soon as a destination is
# selected, shows the A* searching state, then changes to the final
# route analytics when the route is complete.
route_popup_visible = False

last_step_time = 0

# ROUTE ANALYTICS
route_distance_m = 0.0
highway_distance_m = 0.0
weak_distance_m = 0.0
weighted_route_cost = 0.0

# ============================================================
# A* VS DIJKSTRA COMPARISON
# ============================================================

dijkstra_distance_m = 0.0
dijkstra_highway_distance_m = 0.0
dijkstra_weak_distance_m = 0.0
dijkstra_weighted_cost = 0.0
dijkstra_explored_nodes = 0

comparison_available = False
comparison_cost_matches = False
comparison_distance_matches = False

SEARCH_DELAY = 0.08
PATH_DELAY = 0.025

# ============================================================
# LOCATION STATE
# ============================================================

start_location_name = None
goal_location_name = None

start_reference = None
goal_reference = None

# ============================================================
# INTERACTIVE ROAD BLOCKING CONTROLS
# ============================================================

def toggle_block_mode():
    global block_mode

    if searching or path_animation:
        return

    block_mode = not block_mode


def confirm_blocks():
    global block_mode

    if searching or path_animation:
        return

    if pending_block_cells:
        blocked_cells.update(pending_block_cells)
        pending_block_cells.clear()

        # A confirmed map change invalidates any existing route.
        reset_route()

    block_mode = False


def clear_blocks():
    global block_mode

    if searching or path_animation:
        return

    blocked_cells.clear()
    pending_block_cells.clear()
    block_mode = False

    # The next route should be calculated on the newly unblocked map.
    reset_route()


def draw_block_controls():
    """Right panel: clean road-blocking controls."""
    enabled = not searching and not path_animation

    panel = pygame.Rect(
        RIGHT_PANEL_X + 10,
        215,
        RIGHT_PANEL_WIDTH - 20,
        210
    )
    draw_panel_box(panel, "ROAD BLOCKING")

    if block_mode:
        instruction = "BLOCK MODE ACTIVE  •  click road cells"
        instruction_color = (255, 190, 90)
    else:
        instruction = "Select road cells before calculating"
        instruction_color = (190, 195, 202)

    draw_text(
        instruction,
        (panel.x + 16, 253),
        right_hint_font
    )

    buttons = [
        (block_button_rect, "BLOCK ROAD", block_mode),
        (confirm_blocks_rect, "CONFIRM BLOCKS", bool(pending_block_cells)),
        (clear_blocks_rect, "CLEAR ALL BLOCKS", False),
    ]

    for rect, label, active in buttons:
        if not enabled:
            fill = (42, 46, 52)
            border = (70, 74, 80)
            text_color = (125, 130, 136)
        elif active:
            fill = (135, 65, 55)
            border = (255, 150, 120)
            text_color = (255, 245, 240)
        else:
            fill = (45, 50, 58)
            border = (90, 100, 115)
            text_color = (240, 242, 245)

        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 1, border_radius=8)

        surface = popup_small_font.render(
            label,
            True,
            text_color
        )
        screen.blit(
            surface,
            (
                rect.centerx - surface.get_width() // 2,
                rect.centery - surface.get_height() // 2
            )
        )

    # Compact status tiles use the space that was previously wasted by
    # repeated instructional text.
    tile_y = 382
    tile_h = 36
    gap = 10
    tile_w = (panel.width - 32 - gap) // 2

    pending_box = pygame.Rect(
        panel.x + 16,
        tile_y,
        tile_w,
        tile_h
    )
    confirmed_box = pygame.Rect(
        pending_box.right + gap,
        tile_y,
        tile_w,
        tile_h
    )

    for box in (pending_box, confirmed_box):
        pygame.draw.rect(
            screen,
            (24, 30, 38),
            box,
            border_radius=7
        )
        pygame.draw.rect(
            screen,
            (55, 66, 80),
            box,
            1,
            border_radius=7
        )

    draw_text(
        f"PENDING  {len(pending_block_cells)}",
        (pending_box.x + 10, pending_box.y + 9),
        right_section_font
    )
    draw_text(
        f"CONFIRMED  {len(blocked_cells)}",
        (confirmed_box.x + 8, confirmed_box.y + 9),
        right_section_font
    )

def handle_block_map_click(position):
    """Select/deselect one road cell while Block Road mode is active."""
    cell = screen_to_cell(position)

    if cell is None or cell not in road_cells:
        return

    # Do not allow the currently selected endpoints to be blocked.
    if cell == start or cell == goal:
        return

    if cell in pending_block_cells:
        pending_block_cells.remove(cell)
    else:
        pending_block_cells.add(cell)


# ============================================================
# MULTI-STOP ROUTING HELPERS
# ============================================================

def reset_multi_stop_plan():
    global multi_stop_mode, multi_selection_phase
    global multi_route_points, multi_leg_index, multi_leg_paths
    global multi_leg_stats
    global multi_total_distance_m, multi_total_highway_m
    global multi_total_weak_m, multi_total_weighted_cost
    global multi_total_explored, multi_pending_next_leg

    multi_stop_mode = False
    multi_selection_phase = "start"
    multi_route_points = []
    multi_leg_index = 0
    multi_leg_paths = []
    multi_leg_stats = []
    multi_total_distance_m = 0.0
    multi_total_highway_m = 0.0
    multi_total_weak_m = 0.0
    multi_total_weighted_cost = 0.0
    multi_total_explored = 0
    multi_pending_next_leg = False


def start_multi_stop_mode():
    global multi_stop_mode, multi_selection_phase, route_popup_visible
    global popup_route_scroll

    if searching or path_animation:
        return

    reset_route()
    reset_multi_stop_plan()
    multi_stop_mode = True
    multi_selection_phase = "start"
    popup_route_scroll = 0
    route_popup_visible = True


def add_multi_stop():
    global multi_selection_phase

    if not multi_stop_mode or searching or path_animation:
        return

    if multi_route_points:
        multi_selection_phase = "stops"


def set_multi_destination_mode():
    global multi_selection_phase

    if not multi_stop_mode or searching or path_animation:
        return

    if len(multi_route_points) >= 1:
        multi_selection_phase = "destination"


def calculate_multi_stop_route():
    global multi_selection_phase, multi_leg_index
    global multi_leg_paths, multi_leg_stats
    global multi_total_distance_m, multi_total_highway_m
    global multi_total_weak_m, multi_total_weighted_cost
    global multi_total_explored, multi_pending_next_leg

    if (
        not multi_stop_mode
        or searching
        or path_animation
        or len(multi_route_points) < 2
        or multi_selection_phase != "ready"
    ):
        return

    # Start with the first leg. Subsequent legs are launched when
    # the current leg's route animation finishes.
    multi_leg_index = 0
    multi_leg_paths = []
    multi_leg_stats = []
    multi_total_distance_m = 0.0
    multi_total_highway_m = 0.0
    multi_total_weak_m = 0.0
    multi_total_weighted_cost = 0.0
    multi_total_explored = 0
    multi_pending_next_leg = False

    start_name = multi_route_points[0]
    goal_name = multi_route_points[1]
    _set_route_endpoints(start_name, goal_name)
    start_search(start, goal)


def _set_route_endpoints(start_name, goal_name):
    global start_location_name, goal_location_name
    global start_reference, goal_reference, start, goal

    start_location_name = start_name
    goal_location_name = goal_name
    start_reference = location_to_screen(LOCATION_POINTS[start_name])
    goal_reference = location_to_screen(LOCATION_POINTS[goal_name])
    start = LOCATION_ACCESS[start_name]
    goal = LOCATION_ACCESS[goal_name]


def advance_multi_stop_leg():
    global multi_leg_index, multi_pending_next_leg
    global multi_total_distance_m, multi_total_highway_m
    global multi_total_weak_m, multi_total_weighted_cost
    global multi_total_explored

    # Save the completed leg before moving to the next one.
    leg_number = multi_leg_index
    leg_path = list(final_path)
    leg_stats = {
        "from": multi_route_points[leg_number],
        "to": multi_route_points[leg_number + 1],
        "distance": route_distance_m,
        "highway": highway_distance_m,
        "weak": weak_distance_m,
        "cost": weighted_route_cost,
        "explored": len(closed_set),
    }
    multi_leg_paths.append(leg_path)
    multi_leg_stats.append(leg_stats)
    multi_total_distance_m += route_distance_m
    multi_total_highway_m += highway_distance_m
    multi_total_weak_m += weak_distance_m
    multi_total_weighted_cost += weighted_route_cost
    multi_total_explored += len(closed_set)

    multi_leg_index += 1

    if multi_leg_index >= len(multi_route_points) - 1:
        # Entire multi-stop route is complete.
        multi_pending_next_leg = False
        return

    next_start = multi_route_points[multi_leg_index]
    next_goal = multi_route_points[multi_leg_index + 1]
    _set_route_endpoints(next_start, next_goal)
    start_search(start, goal)
    multi_pending_next_leg = False


def draw_multi_stop_controls():
    """Right panel: route controls with no redundant workflow text."""
    enabled = not searching and not path_animation

    panel = pygame.Rect(
        RIGHT_PANEL_X + 10,
        435,
        RIGHT_PANEL_WIDTH - 20,
        355
    )
    draw_panel_box(panel, "ROUTE CONTROLS")

    if multi_stop_mode:
        phase = {
            "start": "START",
            "stops": "ADD STOPS",
            "destination": "DESTINATION",
            "ready": "READY",
        }.get(multi_selection_phase, "MULTI-STOP")
    else:
        phase = "SINGLE ROUTE"

    badge = pygame.Rect(
        panel.right - 125,
        panel.y + 11,
        109,
        22
    )
    pygame.draw.rect(
        screen,
        (32, 40, 50),
        badge,
        border_radius=6
    )
    pygame.draw.rect(
        screen,
        (70, 82, 98),
        badge,
        1,
        border_radius=6
    )

    badge_surface = right_hint_font.render(
        phase,
        True,
        (210, 216, 224)
    )
    screen.blit(
        badge_surface,
        (
            badge.centerx - badge_surface.get_width() // 2,
            badge.y + 4
        )
    )

    buttons = [
        (multi_route_button_rect, "NEW MULTI-STOP PLAN", multi_stop_mode),
        (multi_add_stop_rect, "ADD STOP", multi_selection_phase == "stops"),
        (multi_set_destination_rect, "SET DESTINATION", multi_selection_phase == "destination"),
        (multi_calculate_rect, "CALCULATE ROUTE", multi_selection_phase == "ready"),
    ]

    for rect, label, active in buttons:
        if not enabled:
            fill = (42, 46, 52)
            border = (70, 74, 80)
            text_color = (125, 130, 136)
        elif active:
            fill = (55, 115, 170)
            border = (120, 190, 255)
            text_color = (245, 245, 245)
        else:
            fill = (45, 50, 58)
            border = (90, 100, 115)
            text_color = (240, 242, 245)

        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 1, border_radius=8)

        surface = popup_small_font.render(
            label,
            True,
            text_color
        )
        screen.blit(
            surface,
            (
                rect.centerx - surface.get_width() // 2,
                rect.centery - surface.get_height() // 2
            )
        )

    # Freed space becomes a useful live status area.
    status_box = pygame.Rect(
        panel.x + 16,
        644,
        panel.width - 32,
        146
    )
    pygame.draw.rect(
        screen,
        (10, 14, 20),
        status_box,
        border_radius=9
    )
    pygame.draw.rect(
        screen,
        (82, 96, 112),
        status_box,
        1,
        border_radius=9
    )

    draw_text(
        "LIVE ROUTE STATUS",
        (status_box.x + 12, status_box.y + 10),
        right_section_font
    )

    if searching:
        status = "A* SEARCHING"
        detail = f"Explored {len(closed_set)} nodes"
    elif path_animation:
        status = "DRAWING ROUTE"
        detail = "Final path animation in progress"
    elif multi_stop_mode and multi_selection_phase == "ready":
        status = "MULTI-STOP READY"
        detail = f"{len(multi_route_points)} locations selected"
    elif multi_stop_mode and multi_selection_phase == "start":
        status = "WAITING FOR START"
        detail = "Click a named location on the map"
    elif multi_stop_mode and multi_selection_phase == "stops":
        status = "ADDING STOPS"
        detail = f"{max(0, len(multi_route_points) - 1)} stop(s) selected"
    elif multi_stop_mode and multi_selection_phase == "destination":
        status = "WAITING FOR DESTINATION"
        detail = "Click the final named location"
    elif finished and final_path:
        status = "ROUTE COMPLETE"
        detail = f"Vehicle: {selected_vehicle}"
    else:
        status = "READY"
        detail = "Select locations to begin"

    draw_text(
        status,
        (status_box.x + 12, status_box.y + 34),
        right_section_font
    )
    draw_text(
        detail,
        (status_box.x + 12, status_box.y + 57),
        right_hint_font
    )

    if comparison_available:
        explored_text = (
            f"A* explored: {len(closed_set)}   |   Dijkstra: {dijkstra_explored_nodes}"
        )
        cost_text = (
            f"Cost: A* {weighted_route_cost:.2f}   |   Dijkstra {dijkstra_weighted_cost:.2f}"
        )
        result_text = (
            "RESULT: WEIGHTED COST MATCH"
            if comparison_cost_matches
            else "RESULT: WEIGHTED COST CHECK"
        )

        draw_text(
            explored_text,
            (status_box.x + 12, status_box.y + 73),
            comparison_font
        )
        draw_text(
            cost_text,
            (status_box.x + 12, status_box.y + 89),
            comparison_font
        )
        draw_text(
            result_text,
            (status_box.x + 12, status_box.y + 105),
            popup_small_font
        )

def draw_scrollable_multi_stop_plan(popup):
    # Kept for compatibility with existing state; the new UI does
    # not use a floating or scrollable route popup.
    return


def handle_popup_scroll(mouse_position, wheel_y):
    # Scrolling is no longer needed in the final three-panel layout.
    return


# ============================================================
# RESET
# ============================================================

def reset_route():

    global open_heap
    global came_from
    global g_score

    global start
    global goal
    global current

    global closed_set
    global open_set

    global final_path
    global path_index

    global searching
    global path_animation
    global finished

    global start_location_name
    global goal_location_name

    global start_reference
    global goal_reference
    global route_popup_visible
    global route_distance_m
    global highway_distance_m
    global weak_distance_m
    global weighted_route_cost

    global dijkstra_distance_m
    global dijkstra_highway_distance_m
    global dijkstra_weak_distance_m
    global dijkstra_weighted_cost
    global dijkstra_explored_nodes
    global comparison_available
    global comparison_cost_matches
    global comparison_distance_matches

    open_heap = []
    came_from = {}
    g_score = {}

    start = None
    goal = None
    current = None

    closed_set = set()
    open_set = set()

    final_path = []
    path_index = 0

    searching = False
    path_animation = False
    finished = False

    start_location_name = None
    goal_location_name = None

    start_reference = None
    goal_reference = None
    route_popup_visible = False
    popup_dragging = False
    route_distance_m = 0.0
    highway_distance_m = 0.0
    weak_distance_m = 0.0
    weighted_route_cost = 0.0

    dijkstra_distance_m = 0.0
    dijkstra_highway_distance_m = 0.0
    dijkstra_weak_distance_m = 0.0
    dijkstra_weighted_cost = 0.0
    dijkstra_explored_nodes = 0
    comparison_available = False
    comparison_cost_matches = False
    comparison_distance_matches = False


# ============================================================
# START A* SEARCH
# ============================================================

def start_search(start_cell, goal_cell):

    global open_heap
    global came_from
    global g_score

    global current
    global final_path
    global path_index

    global searching
    global path_animation
    global finished
    global last_step_time
    global route_popup_visible
    global route_distance_m
    global highway_distance_m
    global weak_distance_m
    global weighted_route_cost

    open_heap = []
    came_from = {}

    g_score = {
        start_cell: 0.0
    }

    closed_set.clear()

    open_set.clear()
    open_set.add(start_cell)

    final_path = []
    path_index = 0

    current = None

    searching = True
    path_animation = False
    finished = False
    route_popup_visible = True

    route_distance_m = 0.0
    highway_distance_m = 0.0
    weak_distance_m = 0.0
    weighted_route_cost = 0.0

    last_step_time = time.time()

    first_f = heuristic(
        start_cell,
        goal_cell
    )

    heapq.heappush(
        open_heap,
        (
            first_f,
            0.0,
            start_cell
        )
    )


# ============================================================
# RECONSTRUCT PATH
# ============================================================

def reconstruct_path():

    global final_path
    global path_index

    path = []

    current_node = goal

    path.append(current_node)

    while current_node in came_from:

        current_node = came_from[current_node]

        path.append(current_node)

    path.reverse()

    final_path = path
    path_index = 0


# ============================================================
# ROUTE ANALYTICS
# ============================================================

def calculate_route_statistics():
    global route_distance_m, highway_distance_m, weak_distance_m, weighted_route_cost
    route = highway = weak = 0.0
    for i in range(1, len(final_path)):
        a = final_path[i - 1]
        b = final_path[i]
        dr = abs(b[0] - a[0])
        dc = abs(b[1] - a[1])
        cost = math.sqrt(2) if dr == 1 and dc == 1 else 1.0
        route += cost
        if b in highway_cells:
            highway += cost
        elif b in weak_cells:
            weak += cost
    route_distance_m = route * CELL_SIZE_KM * 1000
    highway_distance_m = highway * CELL_SIZE_KM * 1000
    weak_distance_m = weak * CELL_SIZE_KM * 1000
    # A* stores weighted cost in grid-cell units.
    weighted_route_cost = g_score.get(goal, 0.0)


# ============================================================
# ONE A* SEARCH STEP
# ============================================================

def astar_step():

    global current
    global searching
    global path_animation
    global finished

    if not open_heap:

        searching = False
        finished = True

        return

    f_score, current_g, current_node = heapq.heappop(
        open_heap
    )

    # Ignore outdated heap entries.
    if current_g != g_score.get(
        current_node,
        float("inf")
    ):
        return

    open_set.discard(current_node)

    current = current_node

    if current_node == goal:

        searching = False

        reconstruct_path()
        calculate_route_statistics()

        # Validate the same routing problem with Dijkstra.
        compare_astar_vs_dijkstra()

        path_animation = True

        return

    closed_set.add(current_node)

    for neighbor, movement_cost in get_neighbors(
        current_node
    ):

        if neighbor in closed_set:
            continue

        tentative_g = (
            g_score[current_node]
            +
            movement_cost
        )

        if (
            neighbor not in g_score
            or
            tentative_g < g_score[neighbor]
        ):

            came_from[neighbor] = current_node

            g_score[neighbor] = tentative_g

            h = heuristic(
                neighbor,
                goal
            )

            f = tentative_g + h

            heapq.heappush(
                open_heap,
                (
                    f,
                    tentative_g,
                    neighbor
                )
            )

            open_set.add(neighbor)


# ============================================================
# DRAW CELL
# ============================================================

def draw_cell(
    cell,
    color,
    padding=2
):

    row, col = cell

    x = MAP_X + col * CELL_SIZE
    y = row * CELL_SIZE

    pygame.draw.rect(
        screen,
        color,
        (
            x + padding,
            y + padding,
            CELL_SIZE - padding * 2,
            CELL_SIZE - padding * 2
        )
    )


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(
    text,
    position,
    text_font
):

    surface = text_font.render(
        text,
        True,
        (255, 255, 255)
    )

    screen.blit(
        surface,
        position
    )


# ============================================================
# DRAW ROUTE INFORMATION POPUP
# ============================================================

def draw_popup_text(surface, text, position, text_font, center=False):
    """Draw one line of popup text."""
    text_surface = text_font.render(text, True, (245, 245, 245))
    if center:
        x = position[0] - text_surface.get_width() // 2
    else:
        x = position[0]
    surface.blit(text_surface, (x, position[1]))


def draw_location_markers():
    """Draw named-location reference markers and selected endpoints."""
    # Neutral reference points remain small and unobtrusive.
    for name, point in LOCATION_POINTS.items():
        x, y = location_to_screen(point)

        pygame.draw.circle(
            screen,
            (230, 230, 230),
            (x, y),
            4,
            1
        )

    if start_location_name is not None:
        x, y = location_to_screen(
            LOCATION_POINTS[start_location_name]
        )

        pygame.draw.circle(
            screen,
            (0, 170, 255),
            (x, y),
            11,
            3
        )

    if goal_location_name is not None:
        x, y = location_to_screen(
            LOCATION_POINTS[goal_location_name]
        )

        pygame.draw.circle(
            screen,
            (255, 70, 70),
            (x, y),
            11,
            3
        )


def draw_panel_box(rect, title):
    """Draw a reusable application panel/card."""
    pygame.draw.rect(
        screen,
        (15, 19, 25),
        rect,
        border_radius=12
    )
    pygame.draw.rect(
        screen,
        (70, 80, 95),
        rect,
        1,
        border_radius=12
    )

    draw_text(
        title,
        (rect.x + 16, rect.y + 12),
        popup_font
    )


def draw_route_plan_panel():
    """Left panel: visual delivery itinerary."""
    panel = pygame.Rect(10, 10, LEFT_PANEL_WIDTH - 20, 410)
    draw_panel_box(panel, "ROUTE PLANNER")

    draw_text(
        "Delivery itinerary",
        (panel.x + 16, panel.y + 39),
        popup_small_font
    )

    # Build the ordered locations that are currently known.
    if multi_stop_mode and multi_route_points:
        route_names = list(multi_route_points)
    else:
        route_names = []
        if start_location_name is not None:
            route_names.append(start_location_name)
        if goal_location_name is not None:
            route_names.append(goal_location_name)

    start_y = panel.y + 77
    line_x = panel.x + 24

    # Vertical route line.
    if len(route_names) >= 2:
        pygame.draw.line(
            screen,
            (75, 88, 105),
            (line_x, start_y + 8),
            (line_x, start_y + (len(route_names) - 1) * 36 + 8),
            2
        )

    for index, name in enumerate(route_names):
        y = start_y + index * 36

        if index == 0:
            node_color = (40, 170, 255)
        elif index == len(route_names) - 1:
            node_color = (255, 75, 75)
        else:
            node_color = (255, 190, 50)

        pygame.draw.circle(
            screen,
            node_color,
            (line_x, y + 8),
            8
        )

        if index == 0:
            label = "START"
            label_color = (40, 170, 255)
        elif index == len(route_names) - 1:
            label = "DESTINATION"
            label_color = (255, 100, 100)
        else:
            label = f"STOP {index}"
            label_color = (255, 205, 90)

        draw_text(
            label,
            (panel.x + 43, y - 2),
            popup_small_font
        )
        draw_text(
            name,
            (panel.x + 43, y + 14),
            popup_small_font
        )

    if not route_names:
        draw_text(
            "Select a start location on the map.",
            (panel.x + 43, start_y),
            popup_small_font
        )

    # Bottom instruction strip.
    divider_y = panel.bottom - 62
    pygame.draw.line(
        screen,
        (55, 66, 80),
        (panel.x + 16, divider_y),
        (panel.right - 16, divider_y),
        1
    )

    if multi_stop_mode:
        phase_text = {
            "start": "Choose a start location",
            "stops": "Add stops in visit order",
            "destination": "Choose the final destination",
            "ready": "Plan ready — calculate route",
        }.get(multi_selection_phase, "Multi-stop planning active")
    else:
        phase_text = (
            "Choose a start location"
            if start_location_name is None
            else "Choose a destination"
            if goal_location_name is None
            else "Single route ready"
        )

    draw_text(
        phase_text,
        (panel.x + 16, divider_y + 15),
        popup_small_font
    )

def draw_route_summary_panel():
    """Left panel: route analytics dashboard."""
    panel = pygame.Rect(10, 432, LEFT_PANEL_WIDTH - 20, HEIGHT - 442)
    draw_panel_box(panel, "ROUTE SUMMARY")

    if searching:
        status = "A* SEARCHING"
        status_value = f"Explored {len(closed_set)} nodes"
        status_fill = (65, 85, 105)
    elif path_animation:
        status = "DRAWING ROUTE"
        status_value = f"{len(final_path)} path cells"
        status_fill = (85, 75, 55)
    elif finished and final_path:
        status = (
            "MULTI-STOP COMPLETE"
            if multi_stop_mode and multi_leg_stats
            else "ROUTE COMPLETE"
        )
        status_value = f"Vehicle: {selected_vehicle}"
        status_fill = (45, 95, 72)
    else:
        status = "READY"
        status_value = "Select locations to begin"
        status_fill = (40, 48, 58)

    status_box = pygame.Rect(
        panel.x + 16,
        panel.y + 44,
        panel.width - 32,
        50
    )
    pygame.draw.rect(
        screen,
        status_fill,
        status_box,
        border_radius=8
    )
    draw_text(
        status,
        (status_box.x + 12, status_box.y + 8),
        section_font
    )
    draw_text(
        status_value,
        (status_box.x + 12, status_box.y + 28),
        popup_small_font
    )

    if multi_stop_mode and multi_leg_stats:
        distance = multi_total_distance_m
        cost = multi_total_weighted_cost
        explored = multi_total_explored
        legs = len(multi_leg_stats)
        highway = multi_total_highway_m
        weak = multi_total_weak_m
    else:
        distance = route_distance_m if finished else 0
        cost = weighted_route_cost if finished else 0
        explored = len(closed_set)
        legs = 1 if finished and final_path else 0
        highway = highway_distance_m if finished else 0
        weak = weak_distance_m if finished else 0

    # "Stops" counts only the intermediate delivery points.
    # Start and final destination are intentionally excluded.
    stops = (
        max(0, len(multi_route_points) - 2)
        if multi_stop_mode
        else 0
    )

    cards = [
        ("DISTANCE", f"{distance:.0f} m"),
        ("WEIGHTED COST", f"{cost:.2f}"),
        ("EXPLORED", f"{explored} nodes"),
        ("STOPS", str(stops)),
    ]

    card_w = (panel.width - 48) // 2
    card_h = 62
    cards_top = panel.y + 108

    for index, (label, value) in enumerate(cards):
        col = index % 2
        row = index // 2

        rect = pygame.Rect(
            panel.x + 16 + col * (card_w + 16),
            cards_top + row * (card_h + 10),
            card_w,
            card_h
        )

        pygame.draw.rect(
            screen,
            (24, 30, 38),
            rect,
            border_radius=9
        )
        pygame.draw.rect(
            screen,
            (55, 66, 80),
            rect,
            1,
            border_radius=9
        )

        draw_text(
            label,
            (rect.x + 10, rect.y + 8),
            popup_small_font
        )
        draw_text(
            value,
            (rect.x + 10, rect.y + 30),
            metric_font
        )

    # Road usage section.
    usage_y = cards_top + 142
    draw_text(
        "ROAD USAGE",
        (panel.x + 18, usage_y),
        section_font
    )

    total_physical = highway + weak
    highway_ratio = highway / total_physical if total_physical > 0 else 0
    bar_x = panel.x + 18
    bar_y = usage_y + 28
    bar_w = panel.width - 36
    bar_h = 12

    pygame.draw.rect(
        screen,
        (48, 55, 65),
        (bar_x, bar_y, bar_w, bar_h),
        border_radius=6
    )

    if total_physical > 0:
        pygame.draw.rect(
            screen,
            (80, 150, 210),
            (bar_x, bar_y, int(bar_w * highway_ratio), bar_h),
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            (215, 145, 65),
            (
                bar_x + int(bar_w * highway_ratio),
                bar_y,
                bar_w - int(bar_w * highway_ratio),
                bar_h
            ),
            border_radius=6
        )

    draw_text(
        f"Highway  {highway:.0f} m",
        (panel.x + 18, bar_y + 20),
        popup_small_font
    )
    draw_text(
        f"Weak road  {weak:.0f} m",
        (panel.right - 108, bar_y + 20),
        popup_small_font
    )

    weighted_m = cost * CELL_SIZE_KM * 1000
    draw_text(
        f"Weighted distance equivalent: {weighted_m:.0f} m",
        (panel.x + 18, bar_y + 50),
        popup_small_font
    )

    # The full leg sequence is already represented in Route Planner.

def draw_vehicle_controls():
    """Right panel: polished vehicle selector."""
    panel = pygame.Rect(
        RIGHT_PANEL_X + 10,
        10,
        RIGHT_PANEL_WIDTH - 20,
        205
    )
    draw_panel_box(panel, "VEHICLE PROFILE")

    draw_text(
        "Choose the vehicle used by A*.",
        (panel.x + 16, 40),
        right_hint_font
    )

    button_rects = get_vehicle_button_rects()
    vehicle_button_rects.clear()
    vehicle_button_rects.update(button_rects)

    for name, rect in button_rects.items():
        selected = name == selected_vehicle
        enabled = not searching and not path_animation

        if selected and enabled:
            fill = (55, 115, 170)
            border = (130, 200, 255)
            text_color = (250, 252, 255)
        elif selected:
            fill = (45, 80, 110)
            border = (95, 145, 185)
            text_color = (220, 225, 230)
        elif not enabled:
            fill = (35, 40, 47)
            border = (65, 70, 78)
            text_color = (135, 140, 146)
        else:
            fill = (42, 48, 58)
            border = (85, 95, 110)
            text_color = (240, 242, 245)

        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 1, border_radius=8)

        surface = popup_small_font.render(
            name,
            True,
            text_color
        )
        screen.blit(
            surface,
            (
                rect.centerx - surface.get_width() // 2,
                rect.centery - surface.get_height() // 2
            )
        )

    pygame.draw.line(
        screen,
        (55, 66, 80),
        (panel.x + 16, 150),
        (panel.right - 16, 150),
        1
    )

    draw_text(
        f"Selected vehicle  •  {selected_vehicle}",
        (panel.x + 16, 157),
        right_hint_font
    )

    multiplier_box = pygame.Rect(
        panel.x + 16,
        176,
        panel.width - 32,
        24
    )
    pygame.draw.rect(
        screen,
        (52, 43, 31),
        multiplier_box,
        border_radius=7
    )
    pygame.draw.rect(
        screen,
        (105, 82, 52),
        multiplier_box,
        1,
        border_radius=7
    )

    draw_text(
        f"WEAK ROAD COST     {get_selected_vehicle_multiplier():.2f}×",
        (multiplier_box.x + 10, multiplier_box.y + 3),
        right_section_font
    )

def draw_route_popup():
    """Compatibility wrapper: draw the new left-side information layout."""
    draw_route_plan_panel()
    draw_route_summary_panel()


def select_location(name):
    global start_location_name, goal_location_name
    global start_reference, goal_reference
    global start, goal, final_path, finished, route_popup_visible
    global multi_selection_phase

    point = location_to_screen(LOCATION_POINTS[name])
    road_cell = LOCATION_ACCESS[name]

    # Multi-stop planning mode: clicks build the ordered list instead
    # of immediately launching a single-leg route.
    if multi_stop_mode:
        if multi_selection_phase == "start":
            multi_route_points.clear()
            multi_route_points.append(name)
            multi_selection_phase = "stops"
            _set_route_endpoints(name, name)
            goal = None
            goal_location_name = None
            final_path.clear()
            finished = False
            route_popup_visible = True
            return

        if multi_selection_phase == "stops":
            if name != multi_route_points[-1]:
                multi_route_points.append(name)
            return

        if multi_selection_phase == "destination":
            if len(multi_route_points) >= 1 and name != multi_route_points[-1]:
                multi_route_points.append(name)
                multi_selection_phase = "ready"
            return

        return

    # Original single-route behavior remains unchanged when multi-stop
    # mode is not active.
    if start_location_name is None:
        start_location_name = name
        start_reference = point
        start = road_cell
        goal = None
        goal_location_name = None
        goal_reference = None
        final_path = []
        finished = False
        route_popup_visible = True
        return

    if goal_location_name is None:
        if name == start_location_name:
            return
        goal_location_name = name
        goal_reference = point
        goal = road_cell
        start_search(start, goal)
        return

    start_location_name = name
    start_reference = point
    route_popup_visible = True
    start = road_cell
    goal = None
    goal_location_name = None
    goal_reference = None
    final_path = []
    finished = False


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            # Right click = reset.
            if event.button == 3:

                reset_route()
                pending_block_cells.clear()
                block_mode = False

                continue

            # Left click = popup close, popup drag, or named location.
            if event.button == 1:

                # Road-blocking controls live in the right-side panel.
                if block_button_rect.collidepoint(event.pos):
                    toggle_block_mode()
                    continue

                if confirm_blocks_rect.collidepoint(event.pos):
                    confirm_blocks()
                    continue

                if clear_blocks_rect.collidepoint(event.pos):
                    clear_blocks()
                    continue

                if multi_route_button_rect.collidepoint(event.pos):
                    start_multi_stop_mode()
                    continue

                if multi_add_stop_rect.collidepoint(event.pos):
                    add_multi_stop()
                    continue

                if multi_set_destination_rect.collidepoint(event.pos):
                    set_multi_destination_mode()
                    continue

                if multi_calculate_rect.collidepoint(event.pos):
                    calculate_multi_stop_route()
                    continue

                # Vehicle buttons are in the right panel.
                vehicle_clicked = False
                for vehicle_name, vehicle_rect in vehicle_button_rects.items():
                    if vehicle_rect.collidepoint(event.pos):
                        set_vehicle(vehicle_name)
                        vehicle_clicked = True
                        break

                if vehicle_clicked:
                    continue

                if searching or path_animation:
                    continue

                # Map clicks have two different meanings:
                #   Block mode ON  -> select/deselect a road cell.
                #   Block mode OFF -> select a named location.
                if (
                    MAP_X <= event.pos[0] < MAP_X + WIDTH
                    and 0 <= event.pos[1] < HEIGHT
                ):
                    if block_mode:
                        handle_block_map_click(event.pos)
                    else:
                        location_name = find_clicked_location(
                            event.pos
                        )

                        if location_name is not None:
                            select_location(location_name)

                    continue

        elif event.type == pygame.MOUSEWHEEL:

            handle_popup_scroll(
                pygame.mouse.get_pos(),
                event.y
            )

        elif event.type == pygame.MOUSEMOTION:
            # The final UI uses fixed panels; no floating popup dragging.
            pass

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:
                popup_dragging = False

    # ========================================================
    # ANIMATE A* SEARCH
    # ========================================================

    current_time = time.time()

    if searching:

        if (
            current_time - last_step_time
            >= SEARCH_DELAY
        ):

            astar_step()

            last_step_time = current_time

    # ========================================================
    # ANIMATE FINAL PATH
    # ========================================================

    if path_animation:

        if (
            current_time - last_step_time
            >= PATH_DELAY
        ):

            path_index += 1

            last_step_time = current_time

            if path_index >= len(final_path):

                path_index = len(final_path)

                path_animation = False

                finished = True

                if multi_stop_mode and multi_selection_phase == "ready":
                    if multi_leg_index < len(multi_route_points) - 1:
                        advance_multi_stop_leg()

    # ========================================================
    # DRAW MAP
    # ========================================================

    # Keep the map at its original 800x800 size. The left side is
    # Route Details and the right side contains route controls.
    screen.fill((18, 22, 28))
    screen.blit(
        map_image,
        (MAP_X, 0)
    )

    # Left panel background.
    pygame.draw.rect(
        screen,
        (28, 33, 40),
        (0, 0, LEFT_PANEL_WIDTH, HEIGHT)
    )

    # Right controls panel background.
    pygame.draw.rect(
        screen,
        (28, 33, 40),
        (RIGHT_PANEL_X, 0, RIGHT_PANEL_WIDTH, HEIGHT)
    )


    # Panel dividers keep the three areas visually separate.
    pygame.draw.line(
        screen,
        (65, 72, 82),
        (LEFT_PANEL_WIDTH, 0),
        (LEFT_PANEL_WIDTH, HEIGHT),
        2
    )
    pygame.draw.line(
        screen,
        (65, 72, 82),
        (RIGHT_PANEL_X, 0),
        (RIGHT_PANEL_X, HEIGHT),
        2
    )

    # ========================================================
    # DRAW INTERACTIVE ROAD BLOCKS
    # ========================================================

    for cell in blocked_cells:
        draw_cell(cell, (175, 45, 45), 2)

    for cell in pending_block_cells:
        draw_cell(cell, (255, 120, 70), 1)

    # ========================================================
    # DRAW OPEN SET
    # ========================================================

    for cell in open_set:

        if cell != start and cell != goal:

            draw_cell(
                cell,
                (40, 150, 255),
                3
            )

    # ========================================================
    # DRAW CLOSED SET
    # ========================================================

    for cell in closed_set:

        if cell != start and cell != goal:

            draw_cell(
                cell,
                (150, 80, 180),
                3
            )

    # ========================================================
    # DRAW CURRENT CELL
    # ========================================================

    if current is not None:

        if (
            current != start
            and
            current != goal
        ):

            draw_cell(
                current,
                (255, 165, 0),
                2
            )

    # ========================================================
    # DRAW FINAL ROUTE AS A LINE
    #
    # In multi-stop mode, completed legs stay visible while the
    # current leg animates.
    # ========================================================

    paths_to_draw = []

    if multi_stop_mode and multi_leg_paths:
        paths_to_draw.extend(multi_leg_paths)

    if final_path and path_index > 0:
        paths_to_draw.append(final_path[:path_index + 1])

    for route_path in paths_to_draw:
        points = []
        for row, col in route_path:
            x = MAP_X + col * CELL_SIZE + CELL_SIZE // 2
            y = row * CELL_SIZE + CELL_SIZE // 2
            points.append((x, y))

        if len(points) >= 2:
            pygame.draw.lines(
                screen,
                (255, 230, 0),
                False,
                points,
                4
            )
        elif len(points) == 1:
            pygame.draw.circle(screen, (255, 230, 0), points[0], 3)

    # ========================================================
    # DRAW START / GOAL ROAD CELLS
    # ========================================================

    if start is not None:

        draw_cell(
            start,
            (0, 170, 255),
            1
        )

    if goal is not None:

        draw_cell(
            goal,
            (255, 70, 70),
            1
        )

    # ========================================================
    # DRAW NAMED LOCATION MARKERS
    # ========================================================

    draw_location_markers()

    # Small map legend / live mode indicator.
    if block_mode or multi_stop_mode:
        mode_text = (
            "BLOCK MODE — click road cells"
            if block_mode
            else "MULTI-STOP — follow the planner on the left"
        )
        mode_surface = popup_small_font.render(
            mode_text,
            True,
            (240, 242, 245)
        )
        mode_box = pygame.Rect(
            MAP_X + 14,
            10,
            mode_surface.get_width() + 20,
            24
        )
        pygame.draw.rect(
            screen,
            (18, 23, 30),
            mode_box,
            border_radius=7
        )
        pygame.draw.rect(
            screen,
            (70, 82, 98),
            mode_box,
            1,
            border_radius=7
        )
        screen.blit(
            mode_surface,
            (mode_box.x + 10, mode_box.y + 4)
        )

    # Numbered multi-stop markers make the planned order visible.
    if multi_stop_mode:
        for index, name in enumerate(multi_route_points):
            x, y = location_to_screen(LOCATION_POINTS[name])
            pygame.draw.circle(screen, (255, 190, 50), (x, y), 10, 2)
            number_surface = popup_small_font.render(str(index + 1), True, (255, 255, 255))
            screen.blit(number_surface, (
                x - number_surface.get_width() // 2,
                y - number_surface.get_height() // 2,
            ))

    # ========================================================
    # ROAD BLOCKING CONTROLS
    # ========================================================

    draw_vehicle_controls()
    draw_block_controls()
    draw_multi_stop_controls()

    # ========================================================
    # ROUTE INFORMATION / SUMMARY
    # ========================================================
    # Route information is integrated into the left planning panel;
    # there is no floating popup covering the map.

    draw_route_popup()

    # ========================================================
    # MAP HAS NO BOTTOM STATUS BAR
    # ========================================================
    # The full 800x800 map remains visible so the lower named
    # locations can be selected normally. Route information is
    # already available in the dedicated panel on the right.


    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
