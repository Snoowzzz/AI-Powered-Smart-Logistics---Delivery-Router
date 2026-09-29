import pygame

pygame.init()

# ============================================================
# AI SMART LOGISTICS ROUTER
# v0.8 - 80x80 Road Network Refinement
# ============================================================

WIDTH = 800
MAP_HEIGHT = 800
HUD_HEIGHT = 60
HEIGHT = MAP_HEIGHT + HUD_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "AI Smart Logistics Router - 80x80 Road Refinement"
)

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 22)
small_font = pygame.font.SysFont(None, 17)

# ============================================================
# MAP
# ============================================================

map_image = pygame.image.load("PUBG_Mobile_Livik.jpg")

map_image = pygame.transform.scale(
    map_image,
    (WIDTH, MAP_HEIGHT)
)

# ============================================================
# GRID
# ============================================================

ROWS = 80
COLS = 80

CELL_SIZE = WIDTH // COLS

# ============================================================
# ORIGINAL 40x40 ROAD MASK
# ============================================================
#
# This is the existing road network from v0.6.
#
# # = ROAD
# . = NON-ROAD
#
# We will automatically expand this to 80x80.
# ============================================================

old_road_mask = [
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
# CHECK ORIGINAL MASK
# ============================================================

if len(old_road_mask) != 40:
    raise ValueError(
        f"Expected 40 rows, found {len(old_road_mask)}"
    )

for row_number, row in enumerate(old_road_mask):

    if len(row) != 40:
        raise ValueError(
            f"Row {row_number} has {len(row)} cells instead of 40."
        )

# ============================================================
# CREATE 80x80 ROAD MASK
# ============================================================
#
# Every original 40x40 cell becomes a 2x2 group.
#
# Example:
#
# 40x40:
#
#   .#.
#   .##
#
# becomes:
#
# 80x80:
#
#   ..##
#   ..##
#   ..####
#   ..####
#
# This preserves the existing road network while giving
# us twice the resolution in each direction.
# ============================================================

road_mask = []

for old_row in old_road_mask:

    expanded_row = ""

    for value in old_row:

        if value == "#":

            expanded_row += "##"

        else:

            expanded_row += ".."

    # Each original row becomes two identical rows.
    road_mask.append(expanded_row)
    road_mask.append(expanded_row)

# ============================================================
# CREATE ROAD CELL SET
# ============================================================

road_cells = set()

for row in range(ROWS):

    for col in range(COLS):

        if road_mask[row][col] == "#":

            road_cells.add(
                (row, col)
            )

# ============================================================
# MOUSE → CELL
# ============================================================

def mouse_to_cell(position):

    x, y = position

    # Ignore bottom HUD
    if y >= MAP_HEIGHT:
        return None

    col = x // CELL_SIZE
    row = y // CELL_SIZE

    if 0 <= row < ROWS and 0 <= col < COLS:

        return row, col

    return None


# ============================================================
# TOGGLE ROAD
# ============================================================

def toggle_road(cell):

    if cell in road_cells:

        road_cells.remove(cell)

    else:

        road_cells.add(cell)


# ============================================================
# SAVE 80x80 MASK
# ============================================================

def save_mask():

    filename = "road_mask_80x80.txt"

    with open(filename, "w") as file:

        for row in range(ROWS):

            row_string = ""

            for col in range(COLS):

                if (row, col) in road_cells:

                    row_string += "#"

                else:

                    row_string += "."

            file.write(row_string + "\n")

    print(
        f"Saved 80x80 road mask as {filename}"
    )


# ============================================================
# SAVE SCREENSHOT
# ============================================================

def save_screenshot():

    filename = "Livik_80x80_Road_Marked.png"

    pygame.image.save(
        screen,
        filename
    )

    print(
        f"Saved screenshot as {filename}"
    )


# ============================================================
# CLEAR ALL ROADS
# ============================================================

def clear_roads():

    road_cells.clear()

    print("All road markings cleared.")


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # ----------------------------------------------------
        # MOUSE
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            cell = mouse_to_cell(
                event.pos
            )

            if cell is None:
                continue

            # LEFT CLICK
            #
            # Toggle ROAD / NON-ROAD
            if event.button == 1:

                toggle_road(cell)

            # RIGHT CLICK
            #
            # Remove road marking
            elif event.button == 3:

                road_cells.discard(cell)

        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            # S = save screenshot + mask
            if event.key == pygame.K_s:

                save_screenshot()
                save_mask()

            # M = save only mask
            elif event.key == pygame.K_m:

                save_mask()

            # C = clear everything
            elif event.key == pygame.K_c:

                clear_roads()

            # ESC = quit
            elif event.key == pygame.K_ESCAPE:

                running = False

    # ========================================================
    # DRAW MAP
    # ========================================================

    screen.blit(
        map_image,
        (0, 0)
    )

    # ========================================================
    # DRAW ROAD CELLS
    # ========================================================

    for row, col in road_cells:

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            (220, 60, 60),
            (
                x + 1,
                y + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
        )

    # ========================================================
    # DRAW GRID
    # ========================================================
    #
    # 80x80 means each cell is only 10x10 pixels.
    #
    # A full black grid would make the map difficult to see,
    # so we use thin semi-transparent-looking dark lines by
    # drawing them directly with a subtle color.
    # ========================================================

    for row in range(ROWS + 1):

        y = row * CELL_SIZE

        pygame.draw.line(
            screen,
            (35, 35, 35),
            (0, y),
            (WIDTH, y),
            1
        )

    for col in range(COLS + 1):

        x = col * CELL_SIZE

        pygame.draw.line(
            screen,
            (35, 35, 35),
            (x, 0),
            (x, MAP_HEIGHT),
            1
        )

    # ========================================================
    # HUD
    # ========================================================

    pygame.draw.rect(
        screen,
        (20, 20, 20),
        (
            0,
            MAP_HEIGHT,
            WIDTH,
            HUD_HEIGHT
        )
    )

    # --------------------------------------------------------
    # Instructions
    # --------------------------------------------------------

    text1 = font.render(
        "LEFT CLICK = ROAD / NON-ROAD",
        True,
        (255, 255, 255)
    )

    text2 = small_font.render(
        "RIGHT CLICK = REMOVE ROAD    "
        "S = SAVE    M = SAVE MASK    "
        "C = CLEAR    ESC = QUIT",
        True,
        (200, 200, 200)
    )

    screen.blit(
        text1,
        (10, MAP_HEIGHT + 6)
    )

    screen.blit(
        text2,
        (10, MAP_HEIGHT + 32)
    )

    # --------------------------------------------------------
    # Road counter
    # --------------------------------------------------------

    status = font.render(
        f"Road cells: {len(road_cells)} / {ROWS * COLS}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        status,
        (590, MAP_HEIGHT + 15)
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()