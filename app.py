import pygame
import heapq

pygame.init()

# -----------------------------
# Window / Grid
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

path = []
explored = set()

mode = "obstacle"


# -----------------------------
# Colors
# -----------------------------

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

GREEN = (0, 200, 0)
RED = (200, 0, 0)

BLUE = (100, 180, 255)
YELLOW = (255, 200, 0)


# -----------------------------
# Find valid neighboring cells
# -----------------------------

def get_neighbors(cell):

    row, col = cell

    possible_neighbors = [
        (row - 1, col),  # up
        (row + 1, col),  # down
        (row, col - 1),  # left
        (row, col + 1)   # right
    ]

    valid_neighbors = []

    for neighbor in possible_neighbors:

        n_row, n_col = neighbor

        # Check if inside grid
        if n_row < 0 or n_row >= ROWS:
            continue

        if n_col < 0 or n_col >= COLS:
            continue

        # Check if blocked
        if neighbor in blocked_cells:
            continue

        valid_neighbors.append(neighbor)

    return valid_neighbors


# -----------------------------
# Manhattan heuristic
# -----------------------------

def heuristic(a, b):

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# -----------------------------
# Reconstruct final path
# -----------------------------

def reconstruct_path(came_from, current):

    path = [current]

    while current in came_from:

        current = came_from[current]
        path.append(current)

    path.reverse()

    return path


# -----------------------------
# A* Pathfinding
# -----------------------------

def a_star(start, goal):

    open_heap = []

    heapq.heappush(
        open_heap,
        (0, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    explored = set()

    while open_heap:

        current_f, current = heapq.heappop(open_heap)

        # Ignore cells already processed
        if current in explored:
            continue

        explored.add(current)

        # Goal reached
        if current == goal:

            final_path = reconstruct_path(
                came_from,
                current
            )

            return final_path, explored

        # Check neighbors
        for neighbor in get_neighbors(current):

            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(
                neighbor,
                float("inf")
            ):

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g

                f_score = (
                    tentative_g
                    + heuristic(neighbor, goal)
                )

                heapq.heappush(
                    open_heap,
                    (f_score, neighbor)
                )

    # No route exists
    return [], explored


# -----------------------------
# Main loop
# -----------------------------

running = True

while running:

    for event in pygame.event.get():

        # Quit
        if event.type == pygame.QUIT:
            running = False

        # Keyboard
        elif event.type == pygame.KEYDOWN:

            # Set depot
            if event.key == pygame.K_1:
                mode = "start"

            # Set delivery
            elif event.key == pygame.K_2:
                mode = "goal"

            # Set/remove obstacles
            elif event.key == pygame.K_3:
                mode = "obstacle"

            # Run A*
            elif event.key == pygame.K_SPACE:

                if start is not None and goal is not None:

                    path, explored = a_star(
                        start,
                        goal
                    )

            # Reset
            elif event.key == pygame.K_r:

                blocked_cells.clear()

                start = None
                goal = None

                path = []
                explored = set()

        # Mouse
        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos

            row = mouse_y // CELL_SIZE
            col = mouse_x // CELL_SIZE

            cell = (row, col)

            # -------------------------
            # Start / Depot
            # -------------------------

            if mode == "start":

                start = cell
                blocked_cells.discard(cell)

                path = []
                explored = set()

            # -------------------------
            # Goal / Delivery
            # -------------------------

            elif mode == "goal":

                goal = cell
                blocked_cells.discard(cell)

                path = []
                explored = set()

            # -------------------------
            # Obstacles
            # -------------------------

            elif mode == "obstacle":

                if cell != start and cell != goal:

                    if cell in blocked_cells:

                        blocked_cells.remove(cell)

                    else:

                        blocked_cells.add(cell)

                    path = []
                    explored = set()

    # -----------------------------
    # Draw grid
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

            # Final path
            elif cell in path:

                pygame.draw.rect(
                    screen,
                    YELLOW,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

            # Explored cells
            elif cell in explored:

                pygame.draw.rect(
                    screen,
                    BLUE,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

            # Depot
            elif cell == start:

                pygame.draw.rect(
                    screen,
                    GREEN,
                    (x, y, CELL_SIZE, CELL_SIZE)
                )

            # Delivery
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