import pygame

pygame.init()

# Window settings
WIDTH = 800
HEIGHT = 800

# Grid settings
ROWS = 20
COLS = 20
CELL_SIZE = WIDTH // COLS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router")

clock = pygame.time.Clock()

# Store clicked/blocked cells
blocked_cells = set()

running = True

while running:

    # Handle events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Left mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            col = mouse_x // CELL_SIZE
            row = mouse_y // CELL_SIZE

            blocked_cells.add((row, col))

    # Background
    screen.fill((30, 30, 30))

    # Draw grid
    for row in range(ROWS):
        for col in range(COLS):

            x = col * CELL_SIZE
            y = row * CELL_SIZE

            if (row, col) in blocked_cells:
                color = (80, 80, 80)
            else:
                color = (220, 220, 220)

            pygame.draw.rect(
                screen,
                color,
                (x, y, CELL_SIZE, CELL_SIZE)
            )

            pygame.draw.rect(
                screen,
                (40, 40, 40),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()