import pygame

pygame.init()

# ============================================================
# AI SMART LOGISTICS ROUTER
# v0.6.5 - Interactive road-marking mode
# ============================================================

WIDTH = 800
MAP_HEIGHT = 800
HUD_HEIGHT = 50
HEIGHT = MAP_HEIGHT + HUD_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router - Road Marking")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Livik map
# ------------------------------------------------------------

map_image = pygame.image.load("PUBG_Mobile_Livik.jpg")
map_image = pygame.transform.scale(map_image, (WIDTH, MAP_HEIGHT))

# ------------------------------------------------------------
# 20 x 20 grid
# ------------------------------------------------------------

ROWS = 20
COLS = 20
CELL_SIZE = WIDTH // COLS

# Cells manually marked as NON-ROAD
blocked_cells = set()

font = pygame.font.SysFont(None, 22)
small_font = pygame.font.SysFont(None, 18)


def mouse_to_cell(position):
    """Convert mouse position into (row, col)."""

    x, y = position

    # Ignore clicks inside the bottom instruction bar
    if y >= MAP_HEIGHT:
        return None

    col = x // CELL_SIZE
    row = y // CELL_SIZE

    if 0 <= row < ROWS and 0 <= col < COLS:
        return row, col

    return None


running = True

while running:

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            cell = mouse_to_cell(event.pos)

            if cell is not None:

                # LEFT CLICK:
                # Toggle blocked/unblocked
                if event.button == 1:

                    if cell in blocked_cells:
                        blocked_cells.remove(cell)
                    else:
                        blocked_cells.add(cell)

                # RIGHT CLICK:
                # Always make it unblocked
                elif event.button == 3:

                    blocked_cells.discard(cell)

        elif event.type == pygame.KEYDOWN:

            # Clear all markings
            if event.key == pygame.K_c:
                blocked_cells.clear()

            # Save screenshot
            elif event.key == pygame.K_s:

                filename = "Livik_20x20_Marked.png"

                pygame.image.save(screen, filename)

                print(f"Saved screenshot as {filename}")

            # Quit
            elif event.key == pygame.K_ESCAPE:
                running = False

    # --------------------------------------------------------
    # Draw map
    # --------------------------------------------------------

    screen.blit(map_image, (0, 0))

    # --------------------------------------------------------
    # Draw blocked cells
    # --------------------------------------------------------

    for row, col in blocked_cells:

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            (220, 60, 60),
            (
                x + 2,
                y + 2,
                CELL_SIZE - 3,
                CELL_SIZE - 3
            )
        )

    # --------------------------------------------------------
    # Draw grid - BLACK lines
    # --------------------------------------------------------

    for row in range(ROWS):

        for col in range(COLS):

            x = col * CELL_SIZE
            y = row * CELL_SIZE

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    # --------------------------------------------------------
    # Bottom instruction bar
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        (20, 20, 20),
        (0, MAP_HEIGHT, WIDTH, HUD_HEIGHT)
    )

    text1 = font.render(
        "LEFT CLICK = BLOCK / UNBLOCK",
        True,
        (255, 255, 255)
    )

    text2 = small_font.render(
        "S = screenshot    C = clear    ESC = quit",
        True,
        (200, 200, 200)
    )

    screen.blit(text1, (12, MAP_HEIGHT + 8))
    screen.blit(text2, (12, MAP_HEIGHT + 30))

    # --------------------------------------------------------
    # Blocked counter
    # --------------------------------------------------------

    status = font.render(
        f"Blocked: {len(blocked_cells)} / {ROWS * COLS}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        status,
        (WIDTH - 180, MAP_HEIGHT + 15)
    )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()