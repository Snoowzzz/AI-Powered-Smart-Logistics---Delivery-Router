import pygame

pygame.init()

# -----------------------------
# Window / Grid configuration
# -----------------------------

WIDTH = 800
HEIGHT = 800
ROWS = 20
COLS = 20
CELL_SIZE = WIDTH // COLS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router")

clock = pygame.time.Clock()


# -----------------------------
# Grid state
# -----------------------------

blocked_cells = set()

start = None
goal = None

mode = "obstacle"


# -----------------------------
# Colors
# -----------------------------

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
RED = (200, 0, 0)


# -----------------------------
# Main loop
# -----------------------------

running = True

while running:

    for event in pygame.event.get():

        # Quit
        if event.type == pygame.QUIT:
            running = False

        # Keyboard controls
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:
                mode = "start"

            elif event.key == pygame.K_2:
                mode = "goal"

            elif event.key == pygame.K_3:
                mode = "obstacle"

            elif event.key == pygame.K_r:
                blocked_cells.clear()
                start = None
                goal = None

        # Mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos

            row = mouse_y // CELL_SIZE
            col = mouse_x // CELL_SIZE

            cell = (row, col)

            # -------------------------
            # Set start
            # -------------------------

            if mode == "start":

                # Remove old start
                start = cell

                # A start cannot be an obstacle
                blocked_cells.discard(cell)

            # -------------------------
            # Set goal
            # -------------------------

            elif mode == "goal":

                goal = cell

                # A goal cannot be an obstacle
                blocked_cells.discard(cell)

            # -------------------------
            # Toggle obstacle
            # -------------------------

            elif mode == "obstacle":

                # Don't allow obstacle on start
                # or goal
                if cell != start and cell != goal:

                    if cell in blocked_cells:
                        blocked_cells.remove(cell)
                    else:
                        blocked_cells.add(cell)

    # -----------------------------
    # Drawing
    # -----------------------------

    screen.fill(WHITE)

    for row in range(ROWS):

        for col in range(COLS):

            cell = (row, col)

            x = col * CELL_SIZE
            y = row * CELL_SIZE

            # Obstacle
            if cell in blocked_cells:
                pygame.draw.rect(
                    screen,
                    GRAY,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

            # Start
            elif cell == start:
                pygame.draw.rect(
                    screen,
                    GREEN,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

            # Goal
            elif cell == goal:
                pygame.draw.rect(
                    screen,
                    RED,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

            # Grid lines
            pygame.draw.rect(
                screen,
                BLACK,
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    pygame.display.flip()

    clock.tick(60)


pygame.quit()