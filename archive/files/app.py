import pygame
import heapq
import math
import time

pygame.init()

# ============================================================
# AI SMART LOGISTICS ROUTER
# v0.7 - Named Locations
# ============================================================

WIDTH = 800
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 15)

# ============================================================
# MAP
# ============================================================

map_image = pygame.image.load("PUBG_Mobile_Livik.jpg")

# Keep the original image dimensions so location reference
# points can be scaled correctly to the displayed map.
MAP_ORIGINAL_WIDTH, MAP_ORIGINAL_HEIGHT = map_image.get_size()

map_image = pygame.transform.scale(
    map_image,
    (WIDTH, HEIGHT)
)

# ============================================================
# GRID
# ============================================================

ROWS = 40
COLS = 40

CELL_SIZE = WIDTH // COLS

# ============================================================
# REAL WORLD SCALE
# ============================================================

MAP_SIZE_KM = 2.0
CELL_SIZE_KM = MAP_SIZE_KM / COLS

# ============================================================
# ROAD MASK
# ============================================================

road_mask = [
    ".............................#######....",
    ".........###............#####..#....#...",
    "......###...###...######..#.....#....#..",
    ".....#.........####..#.....###...#...##.",
    "....#..........#.....#........#..#....##",
    "....#..........#......#........#.##....#",
    "...#...........#.....#.........##..#...#",
    "...#........####.....#..........#..#...#",
    "...##....###....#....#...........#.###.#",
    ".....##.##.......#...#............#...#.",
    ".......##........#....#...............#.",
    ".........#.......#....#...............#.",
    ".........#........#....#..............#.",
    "........#.........#....#####.........##.",
    "........#.........#......#..#.......##..",
    ".......###........#......#..##......#...",
    "......#.#.#......##......#...###...#....",
    "....##..##.######..#....#.......###.....",
    "...##.....#....#....#..#......##........",
    "...####........#.....######.##..........",
    "...#...#.......#......#....#.##.........",
    "...#...##......#.......####...#.........",
    "...#....##....##...............#........",
    "...#.....##.##.#...............#........",
    "...#......##...#####......#####.#.......",
    "..#.#.....#.....#..#.....##.....##......",
    "...###....#.....#...#...##........#.....",
    "...#.##..##.....#...#####.......####....",
    "..#...#..#......#...............#..##...",
    ".#....#..#.......##............##...##..",
    ".#.....#..#.....#.###.........#......#..",
    "..#.....####....#...##......##.......#..",
    "..#......#..####......#...###........#..",
    "...#.....#......#......###...........#..",
    "...#...##.......#.......#...........##..",
    "....####........#.......#..........##...",
    "................#........###########....",
    ".............###........................",
    "........................................",
    "........................................",
]

# ============================================================
# CREATE ROAD CELL SET
# ============================================================

road_cells = set()

for row in range(ROWS):
    for col in range(COLS):
        if road_mask[row][col] == "#":
            road_cells.add((row, col))

# ============================================================
# NAMED LOCATIONS
# ============================================================
#
# These are reference points on the original Livik image.
# They are NOT A* nodes.
#
# When the user clicks a named location, the program converts
# the reference point to the current 40x40 grid and finds the
# nearest valid road cell.
#
# Coordinates are approximate map-reference positions, not GPS.
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

LOCATION_NAMES = list(LOCATION_POINTS.keys())

LOCATION_RADIUS = 24


def location_to_screen(point):
    """Convert an original-map pixel point to displayed-map pixels."""

    x, y = point

    screen_x = int(x * WIDTH / MAP_ORIGINAL_WIDTH)
    screen_y = int(y * HEIGHT / MAP_ORIGINAL_HEIGHT)

    return screen_x, screen_y


def screen_to_cell(position):
    """Convert a displayed-map pixel position into a grid cell."""

    x, y = position

    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)

    if 0 <= row < ROWS and 0 <= col < COLS:
        return row, col

    return None


def nearest_road_cell(screen_position):
    """
    Resolve a named location's reference point to the nearest
    traversable road cell.

    The road network is connected in the current mask, so the
    nearest valid road cell is a usable A* node.
    """

    reference_cell = screen_to_cell(screen_position)

    if reference_cell is None:
        return None

    best_cell = None
    best_distance = float("inf")

    for cell in road_cells:

        row, col = cell
        ref_row, ref_col = reference_cell

        distance = math.sqrt(
            (row - ref_row) ** 2 +
            (col - ref_col) ** 2
        )

        if distance < best_distance:
            best_distance = distance
            best_cell = cell

    return best_cell


def find_clicked_location(mouse_position):
    """Return the name of a nearby named location, if any."""

    mouse_x, mouse_y = mouse_position

    best_name = None
    best_distance = float("inf")

    for name, point in LOCATION_POINTS.items():

        location_x, location_y = location_to_screen(point)

        distance = math.sqrt(
            (mouse_x - location_x) ** 2 +
            (mouse_y - location_y) ** 2
        )

        if distance <= LOCATION_RADIUS and distance < best_distance:
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

        new_cell = (new_row, new_col)

        # Stay inside grid
        if not (0 <= new_row < ROWS):
            continue

        if not (0 <= new_col < COLS):
            continue

        # Must be a road
        if new_cell not in road_cells:
            continue

        # Straight movement
        if dr == 0 or dc == 0:
            cost = 1.0

        # Diagonal movement
        else:
            cost = math.sqrt(2)

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

SEARCH_DELAY = 0.08
PATH_DELAY = 0.05

# ============================================================
# LOCATION SELECTION STATE
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

    # Reset everything
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
# ONE A* SEARCH STEP
# ============================================================

def astar_step():

    global current
    global searching
    global path_animation
    global finished

    # Nothing left to search
    if not open_heap:

        searching = False
        finished = True

        return

    # Get best node
    f_score, current_g, current_node = heapq.heappop(
        open_heap
    )

    # Ignore outdated heap entries
    if current_g != g_score.get(
        current_node,
        float("inf")
    ):
        return

    # Remove from open set
    open_set.discard(current_node)

    current = current_node

    # Goal found
    if current_node == goal:

        searching = False

        reconstruct_path()

        path_animation = True

        return

    # Mark as explored
    closed_set.add(current_node)

    # Explore neighbors
    for neighbor, movement_cost in get_neighbors(
        current_node
    ):

        # Don't revisit closed nodes
        if neighbor in closed_set:
            continue

        tentative_g = (
            g_score[current_node]
            +
            movement_cost
        )

        # Better route to neighbor
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
# DRAW LOCATION MARKERS
# ============================================================

def draw_location_markers():

    for name, point in LOCATION_POINTS.items():

        x, y = location_to_screen(point)

        # Small neutral marker showing the clickable reference point.
        pygame.draw.circle(
            screen,
            (230, 230, 230),
            (x, y),
            4,
            1
        )

    # Selected START location
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

    # Selected DESTINATION location
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

    road_cell = nearest_road_cell(point)

    if road_cell is None:
        return

    # FIRST LOCATION = START
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

    # SECOND LOCATION = DESTINATION
    if goal_location_name is None:

        # Don't route from a location to itself.
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

    # THIRD LOCATION = start a new route
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

            # ------------------------------------------------
            # RIGHT CLICK = RESET
            # ------------------------------------------------

            if event.button == 3:

                reset_route()

                continue

            # ------------------------------------------------
            # LEFT CLICK = NAMED LOCATION
            # ------------------------------------------------

            if event.button == 1:

                # Don't allow new selections while searching
                # or while the final route is animating.
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
    # DRAW ROAD CELLS
    # ========================================================
    #
    # TEMPORARY DEBUG VISUALIZATION.
    # We are deliberately keeping this for v0.7.
    # It will be replaced by a cleaner road overlay later.
    # ========================================================

    for row in range(ROWS):

        for col in range(COLS):

            cell = (
                row,
                col
            )

            if cell in road_cells:

                draw_cell(
                    cell,
                    (220, 60, 60),
                    1
                )

    # ========================================================
    # DRAW OPEN SET
    # ========================================================

    for cell in open_set:

        if cell != start and cell != goal:

            draw_cell(
                cell,
                (40, 150, 255),
                4
            )

    # ========================================================
    # DRAW CLOSED SET
    # ========================================================

    for cell in closed_set:

        if cell != start and cell != goal:

            draw_cell(
                cell,
                (150, 80, 180),
                4
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
                3
            )

    # ========================================================
    # DRAW ANIMATED FINAL PATH
    # ========================================================

    if final_path:

        visible_path = final_path[
            :path_index + 1
        ]

        for cell in visible_path:

            if (
                cell != start
                and
                cell != goal
            ):

                draw_cell(
                    cell,
                    (255, 230, 0),
                    3
                )

    # ========================================================
    # DRAW A* START ROAD CELL
    # ========================================================

    if start is not None:

        draw_cell(
            start,
            (0, 170, 255),
            2
        )

    # ========================================================
    # DRAW A* GOAL ROAD CELL
    # ========================================================

    if goal is not None:

        draw_cell(
            goal,
            (255, 70, 70),
            2
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
            760,
            WIDTH,
            40
        )
    )

    # --------------------------------------------------------
    # STATUS MESSAGE
    # --------------------------------------------------------

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
        (10, 768),
        small_font
    )

    # ========================================================
    # SEARCH STATISTICS
    # ========================================================

    explored = len(closed_set)
    frontier = len(open_set)

    if final_path:

        distance_cells = 0

        for i in range(1, len(final_path)):

            r1, c1 = final_path[i - 1]
            r2, c2 = final_path[i]

            dr = abs(r2 - r1)
            dc = abs(c2 - c1)

            if dr == 1 and dc == 1:

                distance_cells += math.sqrt(2)

            else:

                distance_cells += 1

        distance_km = (
            distance_cells
            * CELL_SIZE_KM
        )

        distance_m = (
            distance_km
            * 1000
        )

        stats = (
            f"Explored: {explored}   "
            f"Route: {distance_m:.0f} m"
        )

    else:

        stats = (
            f"Explored: {explored}   "
            f"Open: {frontier}"
        )

    draw_text(
        stats,
        (520, 768),
        small_font
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
