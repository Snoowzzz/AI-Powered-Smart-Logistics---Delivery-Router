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
# Horizontal road
# -----------------------------

for col in range(8, 32):
    road_cells.add((20, col))


# -----------------------------
# Vertical road
# -----------------------------

for row in range(10, 31):
    road_cells.add((row, 20))


# -----------------------------
# Diagonal road
# -----------------------------
# This demonstrates that roads
# can change direction.

for i in range(8):
    road_cells.add((12 + i, 12 + i))


# -----------------------------
# Movement directions
# -----------------------------
# 8 possible directions

directions = [
    (-1, -1),   # Up-left
    (-1,  0),   # Up
    (-1,  1),   # Up-right
    ( 0, -1),   # Left
    ( 0,  1),   # Right
    ( 1, -1),   # Down-left
    ( 1,  0),   # Down
    ( 1,  1),   # Down-right
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

        # Stay inside the grid
        if not (0 <= new_row < ROWS):
            continue

        if not (0 <= new_col < COLS):
            continue

        # Only roads can be visited
        if new_cell not in road_cells:
            continue

        # Calculate movement cost
        if dr != 0 and dc != 0:
            cost = 1.414
        else:
            cost = 1

        neighbors.append((new_cell, cost))

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
    # Draw grid
    # -------------------------

    for row in range(ROWS):

        for col in range(COLS):

            x = col * CELL_SIZE
            y = row * CELL_SIZE

            cell = (row, col)

            # -------------------------
            # Road cell
            # -------------------------

            if cell in road_cells:

                pygame.draw.rect(
                    screen,
                    (0, 255, 0),
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

            # -------------------------
            # Grid line
            # -------------------------

            pygame.draw.rect(
                screen,
                (60, 60, 60),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )


    pygame.display.flip()

    clock.tick(60)


pygame.quit()