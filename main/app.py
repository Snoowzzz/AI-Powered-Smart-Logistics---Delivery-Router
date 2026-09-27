import pygame

pygame.init()

# -----------------------------
# Window
# -----------------------------

WIDTH = 800
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router")

clock = pygame.time.Clock()


# -----------------------------
# Load map
# -----------------------------

map_image = pygame.image.load("PUBG_Mobile_Livik.jpg")

map_image = pygame.transform.scale(
    map_image,
    (WIDTH, HEIGHT)
)


# -----------------------------
# Grid
# -----------------------------

ROWS = 40
COLS = 40

CELL_SIZE = WIDTH // COLS


# -----------------------------
# Road cells
# -----------------------------

road_cells = set()


# -----------------------------
# Add road between two cells
# -----------------------------

def add_road_segment(start, end):

    row1, col1 = start
    row2, col2 = end

    row_distance = row2 - row1
    col_distance = col2 - col1

    steps = max(
        abs(row_distance),
        abs(col_distance)
    )

    if steps == 0:
        road_cells.add(start)
        return

    for i in range(steps + 1):

        t = i / steps

        row = round(
            row1 + row_distance * t
        )

        col = round(
            col1 + col_distance * t
        )

        road_cells.add((row, col))


# -----------------------------
# Add complete road
# -----------------------------

def add_road(waypoints):

    for i in range(len(waypoints) - 1):

        start = waypoints[i]
        end = waypoints[i + 1]

        add_road_segment(start, end)


# =================================================
# REAL LIVIK ROAD NETWORK
# =================================================

# -----------------------------
# Midstein → East Port
# -----------------------------

midstein_east_port = [
    (21, 21),
    (20, 24),
    (19, 27),
    (18, 30),
    (17, 32)
]

add_road(midstein_east_port)


# -----------------------------
# Midstein → Crabgrass
# -----------------------------

midstein_crabgrass = [
    (21, 21),
    (20, 18),
    (19, 15),
    (18, 12),
    (18, 10)
]

add_road(midstein_crabgrass)


# -----------------------------
# Midstein → Reeds
# -----------------------------

midstein_reeds = [
    (21, 21),
    (23, 20),
    (24, 20),
    (26, 19)
]

add_road(midstein_reeds)


# -----------------------------
# Midstein → Power Plant
# -----------------------------

midstein_powerplant = [
    (21, 21),
    (22, 18),
    (23, 15),
    (24, 12),
    (24, 10)
]

add_road(midstein_powerplant)


# -----------------------------
# Midstein → Hot Spring
# -----------------------------

midstein_hot_spring = [
    (21, 21),
    (18, 22),
    (15, 23),
    (12, 24),
    (10, 24)
]

add_road(midstein_hot_spring)


# -----------------------------
# Hot Spring → Rose Farm
# -----------------------------

hot_spring_rose_farm = [
    (10, 24),
    (7, 25),
    (5, 26),
    (3, 27)
]

add_road(hot_spring_rose_farm)


# -----------------------------
# Crabgrass → Blomster
# -----------------------------

crabgrass_blomster = [
    (18, 10),
    (16, 8),
    (13, 7),
    (11, 7)
]

add_road(crabgrass_blomster)


# -----------------------------
# Movement directions
# -----------------------------

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


# -----------------------------
# Get neighbors
# -----------------------------

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

        # Only road cells are allowed
        if new_cell not in road_cells:
            continue

        # Diagonal movement
        if dr != 0 and dc != 0:
            cost = 1.414
        else:
            cost = 1

        neighbors.append(
            (new_cell, cost)
        )

    return neighbors


# -----------------------------
# Main loop
# -----------------------------

running = True

while running:

    # -------------------------
    # Events
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    # -------------------------
    # Draw map
    # -------------------------

    screen.blit(map_image, (0, 0))


    # -------------------------
    # Draw grid and roads
    # -------------------------

    for row in range(ROWS):

        for col in range(COLS):

            x = col * CELL_SIZE
            y = row * CELL_SIZE

            cell = (row, col)

            # -------------------------
            # Road
            # -------------------------

            if cell in road_cells:

                pygame.draw.rect(
                    screen,
                    (0, 255, 0),
                    (
                        x,
                        y,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                )

            # -------------------------
            # Grid
            # -------------------------

            pygame.draw.rect(
                screen,
                (60, 60, 60),
                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                ),
                1
            )


    pygame.display.flip()

    clock.tick(60)


pygame.quit()