import pygame
import heapq
import math
import time

pygame.init()

# ============================================================
# AI SMART LOGISTICS ROUTER
# v0.8.3 - 80x80 Dual Road Network
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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router - v0.8.3")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 15)

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

        if new_cell not in road_cells:
            continue

        if dr == 0 or dc == 0:
            geometric_cost = 1.0
        else:
            geometric_cost = math.sqrt(2)

        if new_cell in highway_cells:
            road_multiplier = 1.0
        elif new_cell in weak_cells:
            road_multiplier = 1.25

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

                continue

            # Left click = named location.
            if event.button == 1:

                if searching or path_animation:
                    continue

                location_name = find_clicked_location(
                    event.pos
                )

                if location_name is not None:

                    select_location(
                        location_name
                    )

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

    screen.blit(
        map_image,
        (0, 0)
    )

    # ========================================================
    # IMPORTANT:
    # NO HIGHWAY/WEAK ROAD BLOCK OVERLAY.
    #
    # The masks are used internally by A*, but the map stays
    # visually clean so the search animation is easy to see.
    # ========================================================

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
    # STATUS BAR
    # ========================================================

    pygame.draw.rect(
        screen,
        (20, 20, 20),
        (
            0,
            730,
            WIDTH,
            70
        )
    )

    if start_location_name is None:

        status = (
            "Click a named location for START"
        )

    elif goal_location_name is None:

        status = (
            f"Start: {start_location_name}  |  "
            "Click a named location for DESTINATION"
        )

    elif searching:

        status = (
            f"{start_location_name} → "
            f"{goal_location_name}  |  "
            "A* is searching..."
        )

    elif path_animation:

        status = (
            f"{start_location_name} → "
            f"{goal_location_name}  |  "
            "Route found — building route..."
        )

    elif finished:

        status = (
            f"{start_location_name} → "
            f"{goal_location_name}  |  "
            "Route complete! Right-click to reset."
        )

    else:

        status = ""

    draw_text(
        status,
        (10, 736),
        small_font
    )

    # ========================================================
    # SEARCH STATISTICS
    # ========================================================

    explored = len(closed_set)
    frontier = len(open_set)

    if final_path:
        stats_line_1 = (
            f"Explored: {explored}   "
            f"Distance: {route_distance_m:.0f} m   "
            f"Weighted Cost: {weighted_route_cost:.2f}"
        )
        stats_line_2 = (
            f"Highway: {highway_distance_m:.0f} m   "
            f"Weak Road: {weak_distance_m:.0f} m"
        )
    else:
        stats_line_1 = f"Explored: {explored}   Open: {frontier}"
        stats_line_2 = ""

    draw_text(stats_line_1, (10, 756), small_font)
    draw_text(stats_line_2, (10, 775), small_font)

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
