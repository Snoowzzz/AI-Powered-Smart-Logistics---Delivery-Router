import pygame
import heapq
import math
import time

pygame.init()


# ============================================================
# WINDOW
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

# Smaller = faster
SEARCH_DELAY = 0.08
PATH_DELAY = 0.05


# ============================================================
# START A* SEARCH
# ============================================================

def start_search(start_cell, goal_cell):

    global open_heap
    global came_from
    global g_score
    global closed_set
    global open_set
    global current
    global final_path
    global path_index
    global searching
    global path_animation
    global finished
    global last_step_time

    start = start_cell

    # Reset everything
    open_heap = []

    came_from = {}

    g_score = {
        start_cell: 0.0
    }

    closed_set = set()

    open_set = {
        start_cell
    }

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

                start = None
                goal = None

                current = None

                open_heap = []

                came_from = {}

                g_score = {}

                open_set = set()

                closed_set = set()

                final_path = []

                path_index = 0

                searching = False
                path_animation = False
                finished = False

                continue


            # ------------------------------------------------
            # LEFT CLICK
            # ------------------------------------------------

            if event.button == 1:

                # Don't allow new selections while searching
                if searching or path_animation:
                    continue

                mouse_x, mouse_y = event.pos

                row = mouse_y // CELL_SIZE
                col = mouse_x // CELL_SIZE

                clicked_cell = (
                    row,
                    col
                )

                # Check grid
                if not (
                    0 <= row < ROWS
                    and
                    0 <= col < COLS
                ):

                    continue

                # Must be road
                if clicked_cell not in road_cells:

                    continue

                # ------------------------------------------------
                # FIRST CLICK
                # ------------------------------------------------

                if start is None:

                    start = clicked_cell

                    goal = None

                    final_path = []

                    finished = False

                # ------------------------------------------------
                # SECOND CLICK
                # ------------------------------------------------

                elif goal is None:

                    goal = clicked_cell

                    start_search(
                        start,
                        goal
                    )

                # ------------------------------------------------
                # THIRD CLICK
                # ------------------------------------------------

                else:

                    start = clicked_cell

                    goal = None

                    final_path = []

                    finished = False


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

    for row in range(ROWS):

        for col in range(COLS):

            cell = (
                row,
                col
            )

            if cell in road_cells:

                # Keep current red road debugging layer
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
    # DRAW START
    # ========================================================

    if start is not None:

        draw_cell(
            start,
            (0, 170, 255),
            2
        )


    # ========================================================
    # DRAW GOAL
    # ========================================================

    if goal is not None:

        draw_cell(
            goal,
            (255, 70, 70),
            2
        )


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

    if start is None:

        status = (
            "Click a ROAD cell for START"
        )

    elif goal is None:

        status = (
            "Click a ROAD cell for DESTINATION"
        )

    elif searching:

        status = (
            "A* is searching..."
        )

    elif path_animation:

        status = (
            "Route found — building route..."
        )

    elif finished:

        status = (
            "Route complete! "
            "Right-click to reset."
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