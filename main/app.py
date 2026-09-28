import pygame
import heapq
import math

pygame.init()

# ============================================================
# WINDOW
# ============================================================

WIDTH = 800
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 22)
small_font = pygame.font.SysFont("Arial", 16)


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
# REAL-WORLD MAP SIZE
# ============================================================
# Livik map is roughly 2 km x 2 km.

MAP_SIZE_KM = 2.0

CELL_SIZE_KM = MAP_SIZE_KM / COLS


# ============================================================
# ROAD MASK
# ============================================================
#
# This comes from the 40x40 road marking you made.
#
# # = ROAD
# . = NOT ROAD
#
# Each string contains exactly 40 cells.
#

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
# CONVERT MASK INTO ROAD CELLS
# ============================================================

road_cells = set()

for row in range(ROWS):

    for col in range(COLS):

        if road_mask[row][col] == "#":
            road_cells.add((row, col))


# ============================================================
# MOVEMENT DIRECTIONS
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


# ============================================================
# GET ROAD NEIGHBORS
# ============================================================

def get_neighbors(cell):

    row, col = cell

    neighbors = []

    for dr, dc in directions:

        new_row = row + dr
        new_col = col + dc

        new_cell = (new_row, new_col)

        # Stay inside the grid
        if not (0 <= new_row < ROWS):
            continue

        if not (0 <= new_col < COLS):
            continue

        # Destination must be a road
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
        (row2 - row1) ** 2 +
        (col2 - col1) ** 2
    )


# ============================================================
# A*
# ============================================================

def a_star(start, goal):

    open_set = []

    heapq.heappush(
        open_set,
        (0, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    while open_set:

        current_f, current = heapq.heappop(open_set)

        # Goal reached
        if current == goal:

            path = []

            while current in came_from:

                path.append(current)
                current = came_from[current]

            path.append(start)

            path.reverse()

            return path, g_score[goal]

        # Explore neighbors
        for neighbor, movement_cost in get_neighbors(current):

            new_g = (
                g_score[current]
                + movement_cost
            )

            if (
                neighbor not in g_score
                or new_g < g_score[neighbor]
            ):

                came_from[neighbor] = current

                g_score[neighbor] = new_g

                f_score = (
                    new_g
                    + heuristic(neighbor, goal)
                )

                heapq.heappush(
                    open_set,
                    (f_score, neighbor)
                )

    # No path found
    return None, None


# ============================================================
# GLOBAL ROUTE STATE
# ============================================================

start = None
goal = None

path = None
path_cost_cells = None

message = "Click a road cell to select START."


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(text, position, font_object):

    surface = font_object.render(
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

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        elif event.type == pygame.MOUSEBUTTONDOWN:

            # --------------------------------------------
            # RIGHT CLICK = RESET
            # --------------------------------------------

            if event.button == 3:

                start = None
                goal = None

                path = None
                path_cost_cells = None

                message = (
                    "Click a road cell to select START."
                )

                continue


            # --------------------------------------------
            # LEFT CLICK
            # --------------------------------------------

            if event.button == 1:

                mouse_x, mouse_y = event.pos

                row = mouse_y // CELL_SIZE
                col = mouse_x // CELL_SIZE

                clicked_cell = (row, col)

                if not (
                    0 <= row < ROWS
                    and
                    0 <= col < COLS
                ):
                    continue

                # Only road cells can be selected
                if clicked_cell not in road_cells:

                    message = "That cell is NOT a road."

                    continue


                # FIRST CLICK = START
                if start is None:

                    start = clicked_cell
                    goal = None
                    path = None
                    path_cost_cells = None

                    message = (
                        "Start selected. "
                        "Click another road cell for DESTINATION."
                    )


                # SECOND CLICK = GOAL
                elif goal is None:

                    goal = clicked_cell

                    path, path_cost_cells = a_star(
                        start,
                        goal
                    )

                    if path is None:

                        message = (
                            "No connected road route found."
                        )

                    else:

                        message = (
                            "Route found! "
                            "Right-click to reset."
                        )


                # THIRD CLICK = NEW START
                else:

                    start = clicked_cell
                    goal = None
                    path = None
                    path_cost_cells = None

                    message = (
                        "New start selected. "
                        "Click destination."
                    )

        # ----------------------------------------------------
        # RIGHT CLICK = RESET
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 3:

                start = None
                goal = None

                path = None
                path_cost_cells = None

                message = (
                    "Click a road cell to select START."
                )


    # ========================================================
    # DRAW MAP
    # ========================================================

    screen.blit(
        map_image,
        (0, 0)
    )


    # ========================================================
    # DRAW ROAD MASK
    # ========================================================

    for row in range(ROWS):

        for col in range(COLS):

            x = col * CELL_SIZE
            y = row * CELL_SIZE

            cell = (row, col)

            # Road cell
            if cell in road_cells:

                pygame.draw.rect(
                    screen,
                    (220, 60, 60),
                    (
                        x,
                        y,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                )

            # Grid
            pygame.draw.rect(
                screen,
                (30, 30, 30),
                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                ),
                1
            )


    # ========================================================
    # DRAW A* ROUTE
    # ========================================================

    if path is not None:

        for row, col in path:

            x = col * CELL_SIZE
            y = row * CELL_SIZE

            pygame.draw.rect(
                screen,
                (255, 230, 0),
                (
                    x + 3,
                    y + 3,
                    CELL_SIZE - 6,
                    CELL_SIZE - 6
                )
            )


    # ========================================================
    # DRAW START
    # ========================================================

    if start is not None:

        row, col = start

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            (0, 150, 255),
            (
                x + 3,
                y + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            )
        )


    # ========================================================
    # DRAW GOAL
    # ========================================================

    if goal is not None:

        row, col = goal

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            (255, 80, 80),
            (
                x + 3,
                y + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            )
        )


    # ========================================================
    # INFORMATION PANEL
    # ========================================================

    pygame.draw.rect(
        screen,
        (20, 20, 20),
        (0, 760, WIDTH, 40)
    )

    draw_text(
        message,
        (10, 768),
        small_font
    )


    # ========================================================
    # ROUTE METRICS
    # ========================================================

    if path is not None:

        distance_km = (
            path_cost_cells
            * CELL_SIZE_KM
        )

        distance_m = distance_km * 1000

        metric_text = (
            f"Distance: {distance_m:.1f} m   "
            f"Cells: {len(path)}"
        )

        draw_text(
            metric_text,
            (500, 768),
            small_font
        )


    pygame.display.flip()

    clock.tick(60)


pygame.quit()