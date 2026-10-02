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
block_button_rect = pygame.Rect(RIGHT_PANEL_X + 20, 290, 150, 38)
confirm_blocks_rect = pygame.Rect(RIGHT_PANEL_X + 185, 290, 155, 38)
clear_blocks_rect = pygame.Rect(RIGHT_PANEL_X + 20, 340, 320, 38)

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

multi_route_button_rect = pygame.Rect(RIGHT_PANEL_X + 20, 505, 320, 38)
multi_add_stop_rect = pygame.Rect(RIGHT_PANEL_X + 20, 550, 155, 38)
multi_set_destination_rect = pygame.Rect(RIGHT_PANEL_X + 185, 550, 155, 38)
multi_calculate_rect = pygame.Rect(RIGHT_PANEL_X + 20, 595, 320, 42)

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
    """Right panel: interactive road blocking."""
    enabled = not searching and not path_animation

    panel = pygame.Rect(
        RIGHT_PANEL_X + 10,
        230,
        RIGHT_PANEL_WIDTH - 20,
        210
    )
    draw_panel_box(panel, "ROAD BLOCKING")

    instruction = (
        "BLOCK MODE: click road cells"
        if block_mode
        else "Block roads before calculating"
    )
    color = (255, 190, 90) if block_mode else (190, 195, 202)

    surface = popup_small_font.render(
        instruction,
        True,
        color
    )
    screen.blit(surface, (panel.x + 16, panel.y + 43))

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

        pygame.draw.rect(
            screen,
            fill,
            rect,
            border_radius=8
        )
        pygame.draw.rect(
            screen,
            border,
            rect,
            1,
            border_radius=8
        )

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

    draw_text(
        f"Pending selections: {len(pending_block_cells)}",
        (panel.x + 16, 342),
        popup_small_font
    )
    draw_text(
        f"Confirmed blocked roads: {len(blocked_cells)}",
        (panel.x + 16, 367),
        popup_small_font
    )
    draw_text(
        "Only road cells can be blocked.",
        (panel.x + 16, 392),
        popup_small_font
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
    """Right panel: multi-stop route planning controls."""
    enabled = not searching and not path_animation

    panel = pygame.Rect(
        RIGHT_PANEL_X + 10,
        455,
        RIGHT_PANEL_WIDTH - 20,
        335
    )
    draw_panel_box(panel, "ROUTE CONTROLS")

    # Buttons are arranged as a simple workflow.
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

        pygame.draw.rect(
            screen,
            fill,
            rect,
            border_radius=8
        )
        pygame.draw.rect(
            screen,
            border,
            rect,
            1,
            border_radius=8
        )

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

    # Workflow text is positioned relative to this panel.
    # The previous version used absolute screen Y values here,
    # which caused the text to overlap the Road Blocking panel.
    workflow_title_y = panel.y + 178

    draw_text(
        "ROUTE WORKFLOW",
        (panel.x + 16, workflow_title_y),
        popup_small_font
    )

    workflow = [
        "1  Start → click a named location",
        "2  Add Stop → click locations in order",
        "3  Set Destination → click final location",
        "4  Calculate Route → A* runs each leg",
    ]

    y = workflow_title_y + 25
    for line in workflow:
        draw_text(
            line,
            (panel.x + 16, y),
            popup_small_font
        )
        y += 23

    status_y = panel.y + 302
    if multi_stop_mode:
        phase = {
            "start": "Waiting for start",
            "stops": "Adding stops",
            "destination": "Waiting for destination",
            "ready": "Ready to calculate",
        }.get(multi_selection_phase, "Multi-stop active")
    else:
        phase = "Single-route mode"

    draw_text(
        f"Status: {phase}",
        (panel.x + 16, status_y),
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
    """Left panel: route planning information and ordered stops."""
    panel = pygame.Rect(10, 10, LEFT_PANEL_WIDTH - 20, 410)
    draw_panel_box(panel, "ROUTE PLANNER")

    y = panel.y + 55

    # Start
    pygame.draw.circle(screen, (40, 170, 255), (panel.x + 22, y + 8), 7)
    draw_text("START", (panel.x + 40, y - 2), popup_small_font)
    start_name = start_location_name or "Select on map"
    draw_text(
        start_name,
        (panel.x + 40, y + 18),
        popup_font
    )
    y += 65

    # Stops
    draw_text("STOPS", (panel.x + 16, y), popup_small_font)
    y += 25

    stop_names = (
        multi_route_points[1:-1]
        if multi_stop_mode and len(multi_route_points) >= 2
        else []
    )

    if stop_names:
        max_visible = 8
        for index, name in enumerate(stop_names[:max_visible], start=1):
            pygame.draw.circle(
                screen,
                (255, 190, 50),
                (panel.x + 22, y + 8),
                7
            )
            draw_text(
                str(index),
                (panel.x + 18, y + 1),
                popup_small_font
            )
            draw_text(
                name,
                (panel.x + 40, y),
                popup_small_font
            )
            y += 28

        if len(stop_names) > max_visible:
            draw_text(
                f"+ {len(stop_names) - max_visible} more stops",
                (panel.x + 40, y),
                popup_small_font
            )
            y += 28
    else:
        draw_text(
            "No stops added",
            (panel.x + 40, y),
            popup_small_font
        )
        y += 28

    y += 8

    # Destination
    pygame.draw.circle(screen, (255, 75, 75), (panel.x + 22, y + 8), 7)
    draw_text("DESTINATION", (panel.x + 40, y - 2), popup_small_font)
    destination_name = (
        multi_route_points[-1]
        if multi_stop_mode and len(multi_route_points) >= 2
        and multi_selection_phase == "ready"
        else goal_location_name or "Select on map"
    )
    draw_text(
        destination_name,
        (panel.x + 40, y + 18),
        popup_font
    )

    # Current mode strip
    mode_y = panel.bottom - 48
    pygame.draw.rect(
        screen,
        (32, 40, 50),
        (panel.x + 14, mode_y, panel.width - 28, 32),
        border_radius=7
    )

    if multi_stop_mode:
        phase_text = {
            "start": "Choose a start location",
            "stops": "Add stops on the map",
            "destination": "Choose final destination",
            "ready": "Plan ready — calculate route",
        }.get(multi_selection_phase, "Multi-stop mode")
    else:
        phase_text = "Single route mode"

    draw_text(
        phase_text,
        (panel.x + 25, mode_y + 8),
        popup_small_font
    )


def draw_route_summary_panel():
    """Left panel: roomy final route statistics."""
    panel = pygame.Rect(10, 432, LEFT_PANEL_WIDTH - 20, HEIGHT - 442)
    draw_panel_box(panel, "ROUTE SUMMARY")

    y = panel.y + 52

    # Current route state
    if searching:
        status = "A* SEARCHING"
        status_value = f"Explored {len(closed_set)} nodes"
    elif path_animation:
        status = "DRAWING ROUTE"
        status_value = f"{len(final_path)} path cells"
    elif finished and final_path:
        status = (
            "MULTI-STOP COMPLETE"
            if multi_stop_mode and multi_leg_stats
            else "ROUTE COMPLETE"
        )
        status_value = f"Vehicle: {selected_vehicle}"
    else:
        status = "READY"
        status_value = "Select locations to begin"

    draw_text(status, (panel.x + 18, y), popup_font)
    draw_text(status_value, (panel.x + 18, y + 24), popup_small_font)
    y += 62

    # Two-column KPI cards
    card_w = (panel.width - 48) // 2
    card_h = 68

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

    cards = [
        ("DISTANCE", f"{distance:.0f} m"),
        ("WEIGHTED COST", f"{cost:.2f}"),
        ("EXPLORED", f"{explored} nodes"),
        ("LEGS", str(legs)),
    ]

    for index, (label, value) in enumerate(cards):
        col = index % 2
        row = index // 2
        rect = pygame.Rect(
            panel.x + 16 + col * (card_w + 16),
            y + row * (card_h + 12),
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
            (rect.x + 10, rect.y + 9),
            popup_small_font
        )
        draw_text(
            value,
            (rect.x + 10, rect.y + 32),
            popup_font
        )

    y += 150

    # Road breakdown
    draw_text("ROAD BREAKDOWN", (panel.x + 18, y), popup_small_font)
    y += 27

    breakdown = [
        ("Highway", highway),
        ("Weak road", weak),
    ]

    for label, value in breakdown:
        draw_text(
            label,
            (panel.x + 20, y),
            popup_small_font
        )
        draw_text(
            f"{value:.0f} m",
            (panel.right - 85, y),
            popup_small_font
        )
        y += 25

    y += 8
    weighted_m = cost * CELL_SIZE_KM * 1000
    draw_text(
        f"Weighted distance equivalent: {weighted_m:.0f} m",
        (panel.x + 18, y),
        popup_small_font
    )

    # Compact leg list — no scrolling required.
    if multi_stop_mode and multi_leg_stats:
        y += 32
        draw_text("COMPLETED LEGS", (panel.x + 18, y), popup_small_font)
        y += 24

        for index, leg in enumerate(multi_leg_stats[:6], start=1):
            draw_text(
                f"{index}. {leg['from']} → {leg['to']}",
                (panel.x + 20, y),
                popup_small_font
            )
            y += 22


def draw_vehicle_controls():
    """Right panel: vehicle selection and current vehicle state."""
    panel = pygame.Rect(
        RIGHT_PANEL_X + 10,
        10,
        RIGHT_PANEL_WIDTH - 20,
        205
    )
    draw_panel_box(panel, "VEHICLE PROFILE")

    draw_text(
        "Choose how weak roads are weighted.",
        (panel.x + 16, 42),
        popup_small_font
    )

    button_rects = get_vehicle_button_rects()
    vehicle_button_rects.clear()
    vehicle_button_rects.update(button_rects)

    for name, rect in button_rects.items():
        selected = name == selected_vehicle
        enabled = not searching and not path_animation

        fill = (55, 115, 170) if selected else (42, 48, 58)
        border = (120, 190, 255) if selected else (85, 95, 110)

        if not enabled:
            fill = (35, 40, 47)
            border = (65, 70, 78)

        pygame.draw.rect(
            screen,
            fill,
            rect,
            border_radius=8
        )
        pygame.draw.rect(
            screen,
            border,
            rect,
            1,
            border_radius=8
        )

        surface = popup_small_font.render(
            name,
            True,
            (245, 245, 245)
        )
        screen.blit(
            surface,
            (
                rect.centerx - surface.get_width() // 2,
                rect.centery - surface.get_height() // 2
            )
        )

    draw_text(
        f"Selected: {selected_vehicle}",
        (panel.x + 16, 151),
        popup_small_font
    )
    draw_text(
        f"Weak-road multiplier: {get_selected_vehicle_multiplier():.2f}×",
        (panel.x + 16, 176),
        popup_small_font
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
    if block_mode:
        draw_text(
            "BLOCK MODE — click road cells",
            (MAP_X + 18, 16),
            popup_small_font
        )
    elif multi_stop_mode:
        draw_text(
            "MULTI-STOP — follow the planner on the left",
            (MAP_X + 18, 16),
            popup_small_font
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
