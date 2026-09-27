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

road_cells = {
    (20, 15),
    (20, 16),
    (20, 17),
    (20, 18),
    (20, 19),
}


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