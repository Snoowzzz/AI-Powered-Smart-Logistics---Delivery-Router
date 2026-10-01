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
WINDOW_WIDTH = 1180

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
POPUP_X = WIDTH + 20
POPUP_Y = 18

# The popup can be moved by dragging its header. These values are
# deliberately kept as separate state so the popup can be repositioned
# without affecting the map or routing logic.
popup_dragging = False
popup_drag_offset_x = 0
popup_drag_offset_y = 0

# ============================================================
# INTERACTIVE ROAD BLOCKING — STAGE 3
# ============================================================
# Users can select multiple road cells, review them, and then
# confirm the blocks. Confirmed blocks are excluded by A*.
blocked_cells = set()
pending_block_cells = set()
block_mode = False
block_button_rect = pygame.Rect(WIDTH + 20, 515, 160, 38)
confirm_blocks_rect = pygame.Rect(WIDTH + 195, 515, 145, 38)
clear_blocks_rect = pygame.Rect(WIDTH + 20, 565, 320, 38)

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

def get_popup_vehicle_button_rects():
    # Four compact buttons across the popup.
    names = list(VEHICLE_PROFILES.keys())
    rects = {}
    button_y = POPUP_Y + 135
    gap = 8
    left = POPUP_X + 18
    total_width = POPUP_WIDTH - 36
    button_width = (total_width - gap * (len(names) - 1)) // len(names)
    for index, name in enumerate(names):
        rects[name] = pygame.Rect(
            left + index * (button_width + gap),
            button_y,
            button_width,
            34
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
    x = max(WIDTH + 10, min(x, WINDOW_WIDTH - POPUP_WIDTH - 10))
    y = max(0, min(y, HEIGHT - POPUP_HEIGHT))
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

    screen_x = int(
        x * WIDTH / MAP_ORIGINAL_WIDTH
    )

    screen_y = int(
        y * HEIGHT / MAP_ORIGINAL_HEIGHT
    )

    return screen_x, screen_y


def screen_to_cell(position):
    """Convert displayed-map pixels to an 80x80 cell."""

    x, y = position

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
    enabled = not searching and not path_animation

    # Section title
    draw_text("ROAD BLOCKING", (WIDTH + 20, 475), popup_font)

    if block_mode:
        instruction = "BLOCK MODE: click road cells"
        instruction_color = (255, 190, 90)
    else:
        instruction = "Block roads before starting a route"
        instruction_color = (190, 195, 202)

    instruction_surface = popup_small_font.render(
        instruction, True, instruction_color
    )
    screen.blit(instruction_surface, (WIDTH + 20, 495))

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

        pygame.draw.rect(screen, fill, rect, border_radius=7)
        pygame.draw.rect(screen, border, rect, 1, border_radius=7)

        text_surface = popup_small_font.render(label, True, text_color)
        screen.blit(
            text_surface,
            (
                rect.centerx - text_surface.get_width() // 2,
                rect.centery - text_surface.get_height() // 2,
            )
        )

    status = (
        f"Pending: {len(pending_block_cells)}   "
        f"Blocked: {len(blocked_cells)}"
    )
    status_surface = popup_small_font.render(
        status, True, (200, 205, 212)
    )
    screen.blit(status_surface, (WIDTH + 20, 618))

    hint = "Only road cells can be blocked."
    hint_surface = popup_small_font.render(
        hint, True, (155, 160, 168)
    )
    screen.blit(hint_surface, (WIDTH + 20, 642))


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

    x = col * CELL_SIZE
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


def draw_route_popup():
    """Draw the draggable route/search/vehicle information panel."""
    if not route_popup_visible:
        return

    popup_rect = get_popup_rect()
    close_rect = get_popup_close_rect()

    popup = pygame.Surface(
        (POPUP_WIDTH, POPUP_HEIGHT),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        popup,
        (12, 16, 22, 238),
        popup.get_rect(),
        border_radius=14
    )
    pygame.draw.rect(
        popup,
        (90, 100, 115, 255),
        popup.get_rect(),
        2,
        border_radius=14
    )

    # Header / drag handle
    draw_popup_text(
        popup,
        "ROUTE DETAILS",
        (18, 16),
        popup_title_font
    )
    draw_popup_text(
        popup,
        "Drag header to move",
        (18, 39),
        popup_small_font
    )

    close_local = pygame.Rect(
        close_rect.x - POPUP_X,
        close_rect.y - POPUP_Y,
        close_rect.width,
        close_rect.height
    )
    pygame.draw.rect(
        popup,
        (45, 50, 58, 255),
        close_local,
        border_radius=7
    )
    pygame.draw.line(
        popup, (220, 220, 220),
        (close_local.x + 8, close_local.y + 8),
        (close_local.right - 8, close_local.bottom - 8),
        2
    )
    pygame.draw.line(
        popup, (220, 220, 220),
        (close_local.right - 8, close_local.y + 8),
        (close_local.x + 8, close_local.bottom - 8),
        2
    )

    if start_location_name is not None:
        draw_popup_text(
            popup,
            f"From: {start_location_name}",
            (18, 66),
            popup_font
        )

    if goal_location_name is not None:
        draw_popup_text(
            popup,
            f"To: {goal_location_name}",
            (18, 91),
            popup_font
        )
    else:
        draw_popup_text(
            popup,
            "To: Select destination on map",
            (18, 91),
            popup_small_font
        )

    pygame.draw.line(
        popup,
        (75, 82, 92),
        (18, 116),
        (POPUP_WIDTH - 18, 116),
        1
    )

    # Vehicle selection is available before the search starts.
    draw_popup_text(
        popup,
        "Vehicle",
        (18, 126),
        popup_small_font
    )

    button_rects = get_popup_vehicle_button_rects()
    vehicle_button_rects.clear()
    vehicle_button_rects.update(button_rects)

    for vehicle_name, rect in button_rects.items():
        local = rect.move(-POPUP_X, -POPUP_Y)
        selected = vehicle_name == selected_vehicle
        enabled = not searching and not path_animation
        fill = (55, 115, 170, 255) if selected else (45, 50, 58, 255)
        border = (120, 190, 255, 255) if selected else (90, 100, 115, 255)
        if not enabled:
            fill = (38, 42, 48, 255)
            border = (65, 70, 78, 255)
        pygame.draw.rect(popup, fill, local, border_radius=7)
        pygame.draw.rect(popup, border, local, 1, border_radius=7)
        text_color = (245, 245, 245) if enabled or selected else (150, 155, 160)
        text_surface = popup_small_font.render(vehicle_name, True, text_color)
        popup.blit(
            text_surface,
            (
                local.centerx - text_surface.get_width() // 2,
                local.centery - text_surface.get_height() // 2
            )
        )

    draw_popup_text(
        popup,
        f"Weak-road multiplier: {get_selected_vehicle_multiplier():.2f}",
        (18, 178),
        popup_small_font
    )
    draw_popup_text(
        popup,
        f"Blocked roads: {len(blocked_cells)}",
        (18, 195),
        popup_small_font
    )

    pygame.draw.line(
        popup,
        (75, 82, 92),
        (18, 220),
        (POPUP_WIDTH - 18, 220),
        1
    )

    explored = len(closed_set)
    frontier = len(open_set)

    if start_location_name is not None and goal_location_name is None:
        draw_popup_text(
            popup,
            "Select a destination to start A*.",
            (18, 239),
            popup_font
        )
        draw_popup_text(
            popup,
            "Vehicle selection will be used for the route.",
            (18, 273),
            popup_small_font
        )

    elif searching:
        draw_popup_text(
            popup,
            "A* is searching...",
            (18, 239),
            popup_font
        )
        draw_popup_text(
            popup,
            f"Explored nodes: {explored}",
            (18, 273),
            popup_small_font
        )
        draw_popup_text(
            popup,
            f"Open set: {frontier}",
            (18, 296),
            popup_small_font
        )
        draw_popup_text(
            popup,
            "Vehicle selection is locked during search.",
            (18, 333),
            popup_small_font
        )

    elif path_animation:
        draw_popup_text(
            popup,
            "Route found — drawing route...",
            (18, 222),
            popup_font
        )
        draw_popup_text(
            popup,
            f"Explored nodes: {explored}",
            (18, 256),
            popup_small_font
        )

    elif finished and final_path:
        draw_popup_text(
            popup,
            "Route complete",
            (18, 222),
            popup_font
        )
        draw_popup_text(
            popup,
            f"Vehicle: {selected_vehicle}",
            (18, 250),
            popup_small_font
        )
        draw_popup_text(
            popup,
            f"Explored: {explored}",
            (18, 276),
            popup_small_font
        )
        draw_popup_text(
            popup,
            f"Distance: {route_distance_m:.0f} m",
            (18, 299),
            popup_small_font
        )
        draw_popup_text(
            popup,
            f"Weighted Cost: {weighted_route_cost:.2f}",
            (18, 322),
            popup_small_font
        )
        draw_popup_text(
            popup,
            f"Highway: {highway_distance_m:.0f} m",
            (18, 345),
            popup_small_font
        )
        draw_popup_text(
            popup,
            f"Weak Road: {weak_distance_m:.0f} m",
            (18, 368),
            popup_small_font
        )
        pygame.draw.line(
            popup,
            (75, 82, 92),
            (18, 397),
            (POPUP_WIDTH - 18, 397),
            1
        )
        draw_popup_text(
            popup,
            "Select a new location to start another route.",
            (18, 410),
            popup_small_font
        )

    screen.blit(popup, (POPUP_X, POPUP_Y))


# ============================================================
# DRAW NAMED LOCATION MARKERS
# ============================================================

def draw_location_markers():

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


# ============================================================
# SELECT NAMED LOCATION
# ============================================================

def select_location(name):

    global start_location_name
    global goal_location_name

    global start_reference
    global goal_reference

    global start
    global goal
    global final_path
    global finished
    global route_popup_visible

    point = location_to_screen(
        LOCATION_POINTS[name]
    )

    # Use the exact access cell selected for this named location.
    # No nearest-road guessing is used anymore.
    road_cell = LOCATION_ACCESS[name]

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

        start_search(
            start,
            goal
        )

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

                # While Block Road mode is active, map clicks are used
                # only for selecting road cells, not named locations.
                if block_mode and event.pos[0] < WIDTH and event.pos[1] < HEIGHT:
                    if not searching and not path_animation:
                        handle_block_map_click(event.pos)
                    continue

                if route_popup_visible:

                    if get_popup_close_rect().collidepoint(event.pos):
                        route_popup_visible = False
                        continue

                    if get_popup_header_rect().collidepoint(event.pos):
                        popup_dragging = True
                        popup_drag_offset_x = event.pos[0] - POPUP_X
                        popup_drag_offset_y = event.pos[1] - POPUP_Y
                        continue

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

                location_name = find_clicked_location(
                    event.pos
                )

                if location_name is not None:

                    select_location(
                        location_name
                    )

        elif event.type == pygame.MOUSEMOTION:

            if popup_dragging:
                POPUP_X, POPUP_Y = clamp_popup_position(
                    event.pos[0] - popup_drag_offset_x,
                    event.pos[1] - popup_drag_offset_y
                )

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

    # ========================================================
    # DRAW MAP
    # ========================================================

    # Keep the map at its original 800x800 size. The right side is
    # a separate UI area for Route Details and does not affect routing.
    screen.fill((18, 22, 28))
    screen.blit(
        map_image,
        (0, 0)
    )

    pygame.draw.rect(
        screen,
        (28, 33, 40),
        (WIDTH, 0, WINDOW_WIDTH - WIDTH, HEIGHT)
    )

    side_title = popup_title_font.render(
        "ROUTE PANEL", True, (220, 225, 232)
    )
    screen.blit(side_title, (WIDTH + 20, 770))

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
    # No yellow route blocks.
    # The route is drawn as a connected line over the map.
    # ========================================================

    if final_path and path_index > 0:

        visible_path = final_path[
            :path_index + 1
        ]

        points = []

        for row, col in visible_path:

            x = (
                col * CELL_SIZE
                +
                CELL_SIZE // 2
            )

            y = (
                row * CELL_SIZE
                +
                CELL_SIZE // 2
            )

            points.append(
                (x, y)
            )

        if len(points) >= 2:

            pygame.draw.lines(
                screen,
                (255, 230, 0),
                False,
                points,
                4
            )

        elif len(points) == 1:

            pygame.draw.circle(
                screen,
                (255, 230, 0),
                points[0],
                3
            )

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

    # ========================================================
    # ROAD BLOCKING CONTROLS
    # ========================================================

    draw_block_controls()

    # ========================================================
    # ROUTE INFORMATION POPUP
    # ========================================================
    # The popup lives in the dedicated panel to the right of the map.
    # It remains draggable within that panel.

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
