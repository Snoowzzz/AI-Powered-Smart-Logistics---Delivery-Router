import pygame
from pathlib import Path

pygame.init()

# ============================================================
# AI SMART LOGISTICS ROUTER
# v0.8.2 - Highway + Weak/Muddy Road Marking (No Grid)
# ============================================================

WIDTH = 800
MAP_HEIGHT = 800
HUD_HEIGHT = 60
HEIGHT = MAP_HEIGHT + HUD_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Smart Logistics Router - Road Network Marking (No Grid)")

clock = pygame.time.Clock()

# ============================================================
# MAP
# ============================================================

map_image = pygame.image.load("PUBG_Mobile_Livik.jpg")
map_image = pygame.transform.scale(map_image, (WIDTH, MAP_HEIGHT))

# ============================================================
# 80 x 80 GRID
# ============================================================

ROWS = 80
COLS = 80
CELL_SIZE = WIDTH // COLS

# ============================================================
# FILES
# ============================================================

HIGHWAY_MASK_FILE = "road_mask_80x80.txt"
WEAK_MASK_FILE = "weak_road_mask_80x80.txt"

# ============================================================
# COLORS
# ============================================================

HIGHWAY_COLOR = (220, 60, 60)       # Red
WEAK_COLOR = (210, 150, 40)         # Orange/brown
GRID_COLOR = (0, 0, 0)
HUD_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
LIGHT_TEXT = (210, 210, 210)

# ============================================================
# FONTS
# ============================================================

font = pygame.font.SysFont(None, 22)
small_font = pygame.font.SysFont(None, 18)

# ============================================================
# ROAD NETWORK
# ============================================================
# Highway mask is loaded from the finished 80x80 network.
# Weak/muddy roads start empty and will be painted manually.
# '#' = road
# '.' = non-road
# ============================================================


def load_mask(filename):
    """Load an 80x80 road mask from a text file."""

    path = Path(filename)

    if not path.exists():
        print(f"ERROR: Could not find {filename}")
        pygame.quit()
        raise SystemExit

    with path.open("r", encoding="utf-8") as file:
        rows = [line.rstrip("\n\r") for line in file]

    if len(rows) != ROWS:
        print(
            f"ERROR: {filename} must contain {ROWS} rows, "
            f"but contains {len(rows)}."
        )
        pygame.quit()
        raise SystemExit

    for index, row in enumerate(rows):
        if len(row) != COLS:
            print(
                f"ERROR: Row {index + 1} of {filename} must contain "
                f"{COLS} characters, but contains {len(row)}."
            )
            pygame.quit()
            raise SystemExit

        if any(char not in ".#" for char in row):
            print(
                f"ERROR: Row {index + 1} of {filename} contains "
                "characters other than '.' and '#'."
            )
            pygame.quit()
            raise SystemExit

    return {
        (row, col)
        for row in range(ROWS)
        for col in range(COLS)
        if rows[row][col] == "#"
    }


def save_mask(filename, cells):
    """Save a cell set as an 80x80 '#' / '.' mask."""

    lines = []

    for row in range(ROWS):
        line = ""

        for col in range(COLS):
            line += "#" if (row, col) in cells else "."

        lines.append(line)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print(f"Saved {filename}")


# Load the finished highway network.
highway_cells = load_mask(HIGHWAY_MASK_FILE)

# Weak/muddy roads start empty.
weak_cells = set()

# ============================================================
# EDIT MODE
# ============================================================
# 1 = HIGHWAY MODE
# 2 = WEAK / MUDDY ROAD MODE
# ============================================================

EDIT_HIGHWAY = 1
EDIT_WEAK = 2
edit_mode = EDIT_HIGHWAY

# ============================================================
# MOUSE -> CELL
# ============================================================


def mouse_to_cell(position):
    """Convert mouse position into (row, col)."""

    x, y = position

    if y >= MAP_HEIGHT:
        return None

    col = x // CELL_SIZE
    row = y // CELL_SIZE

    if 0 <= row < ROWS and 0 <= col < COLS:
        return row, col

    return None


# ============================================================
# SAVE EVERYTHING
# ============================================================


def save_all():

    save_mask(HIGHWAY_MASK_FILE, highway_cells)
    save_mask(WEAK_MASK_FILE, weak_cells)

    screenshot_name = "Livik_80x80_Road_Network.png"
    pygame.image.save(screen, screenshot_name)

    print(f"Saved screenshot as {screenshot_name}")


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

            cell = mouse_to_cell(event.pos)

            if cell is None:
                continue

            # HIGHWAY MODE
            if edit_mode == EDIT_HIGHWAY:

                # LEFT = toggle highway
                if event.button == 1:

                    if cell in highway_cells:
                        highway_cells.remove(cell)
                    else:
                        highway_cells.add(cell)
                        # A cell cannot be both highway and weak.
                        weak_cells.discard(cell)

                # RIGHT = remove highway
                elif event.button == 3:
                    highway_cells.discard(cell)

            # WEAK / MUDDY MODE
            elif edit_mode == EDIT_WEAK:

                # LEFT = toggle weak road
                if event.button == 1:

                    # Never allow weak road on a highway cell.
                    if cell in highway_cells:
                        continue

                    if cell in weak_cells:
                        weak_cells.remove(cell)
                    else:
                        weak_cells.add(cell)

                # RIGHT = remove weak road
                elif event.button == 3:
                    weak_cells.discard(cell)

        elif event.type == pygame.KEYDOWN:

            # 1 = HIGHWAY MODE
            if event.key == pygame.K_1:
                edit_mode = EDIT_HIGHWAY
                print("EDIT MODE: HIGHWAY")

            # 2 = WEAK / MUDDY MODE
            elif event.key == pygame.K_2:
                edit_mode = EDIT_WEAK
                print("EDIT MODE: WEAK / MUDDY ROAD")

            # S = screenshot + save both masks
            elif event.key == pygame.K_s:
                save_all()

            # M = save only both masks
            elif event.key == pygame.K_m:
                save_mask(HIGHWAY_MASK_FILE, highway_cells)
                save_mask(WEAK_MASK_FILE, weak_cells)

            # C = clear current edit layer
            elif event.key == pygame.K_c:

                if edit_mode == EDIT_HIGHWAY:
                    highway_cells.clear()
                    print("Highway layer cleared.")
                else:
                    weak_cells.clear()
                    print("Weak/muddy road layer cleared.")

            # ESC = quit
            elif event.key == pygame.K_ESCAPE:
                running = False

    # ========================================================
    # DRAW MAP
    # ========================================================

    screen.blit(map_image, (0, 0))

    # ========================================================
    # DRAW HIGHWAYS
    # ========================================================

    for row, col in highway_cells:

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            HIGHWAY_COLOR,
            (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        )

    # ========================================================
    # DRAW WEAK / MUDDY ROADS
    # ========================================================

    for row, col in weak_cells:

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            WEAK_COLOR,
            (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        )

    # ========================================================
    # HUD
    # ========================================================

    pygame.draw.rect(
        screen,
        HUD_COLOR,
        (0, MAP_HEIGHT, WIDTH, HUD_HEIGHT)
    )

    if edit_mode == EDIT_HIGHWAY:
        mode_text = "MODE 1: HIGHWAY"
        mode_color = HIGHWAY_COLOR
    else:
        mode_text = "MODE 2: WEAK / MUDDY ROAD"
        mode_color = WEAK_COLOR

    mode_surface = font.render(
        mode_text,
        True,
        mode_color
    )

    screen.blit(
        mode_surface,
        (10, MAP_HEIGHT + 7)
    )

    instructions = small_font.render(
        "1 = highway   2 = weak/muddy   "
        "LEFT = toggle   RIGHT = remove   "
        "S = save   M = masks   C = clear layer   ESC = quit",
        True,
        LIGHT_TEXT
    )

    screen.blit(
        instructions,
        (10, MAP_HEIGHT + 31)
    )

    counter = small_font.render(
        f"Highway: {len(highway_cells)}    "
        f"Weak: {len(weak_cells)}    "
        f"Total: {len(highway_cells) + len(weak_cells)}",
        True,
        WHITE
    )

    counter_rect = counter.get_rect(
        topright=(WIDTH - 10, MAP_HEIGHT + 9)
    )

    screen.blit(counter, counter_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
