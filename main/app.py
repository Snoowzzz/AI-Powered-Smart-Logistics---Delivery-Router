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

            pygame.draw.rect(
                screen,
                (60, 60, 60),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    pygame.display.flip()

    clock.tick(60)


pygame.quit()