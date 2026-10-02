import pygame
from pathlib import Path

pygame.init()

# ============================================================
# AI SMART LOGISTICS ROUTER
# LOCATION ACCESS POINT MARKER
# ============================================================
# Purpose:
#   Mark one exact road cell for every named Livik location.
#
# The access cell can ONLY be:
#   1. Highway cell
#   2. Weak / muddy road cell
#
# Existing highway and weak-road masks are NEVER modified here.
#
# Controls:
#   LEFT CLICK near a named location = select that location
#   LEFT CLICK on a road cell = assign that cell to selected location
#   C = confirm/save the current location and move to the next one
#   RIGHT CLICK on an assigned access cell = remove assignment
#   S = save access-point file + screenshot
#   M = save access-point file
#   ESC = quit
# ============================================================


# ============================================================
# WINDOW
# ============================================================

WIDTH = 800
MAP_HEIGHT = 800
HUD_HEIGHT = 70
HEIGHT = MAP_HEIGHT + HUD_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "AI Smart Logistics Router - Location Access Point Marker"
)

clock = pygame.time.Clock()


# ============================================================
# MAP
# ============================================================

map_image = pygame.image.load("PUBG_Mobile_Livik.jpg")
map_image = pygame.transform.scale(
    map_image,
    (WIDTH, MAP_HEIGHT)
)

MAP_ORIGINAL_WIDTH, MAP_ORIGINAL_HEIGHT = map_image.get_size()


# ============================================================
# GRID
# ============================================================

ROWS = 80
COLS = 80
CELL_SIZE = WIDTH // COLS


# ============================================================
# ROAD MASK FILES
# ============================================================

HIGHWAY_MASK_FILE = "road_mask_80x80.txt"
WEAK_MASK_FILE = "weak_road_mask_80x80.txt"

ACCESS_FILE = "location_access_points.txt"


# ============================================================
# COLORS
# ============================================================

HIGHWAY_COLOR = (220, 60, 60)
WEAK_COLOR = (210, 150, 40)

ACCESS_COLOR = (0, 255, 255)
SELECTED_COLOR = (255, 255, 255)

LOCATION_COLOR = (255, 255, 255)

HUD_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
LIGHT_TEXT = (210, 210, 210)

ERROR_COLOR = (255, 80, 80)


# ============================================================
# FONTS
# ============================================================

font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 15)


# ============================================================
# NAMED LOCATIONS
# ============================================================

LOCATION_POINTS = {
    "Wengen": (109.8, 79.6),
    "Gass": (276.2, 79.6),
    "Rose Farm": (429.5, 44.6),
    "Iceborg": (594.2, 119.9),
    "Lupin Felt": (133.3, 133.9),
    "Hot Spring": (470.5, 180.3),
    "Blomster": (135.0, 225.8),
    "Gronhus": (299.7, 224.9),
    "Crabgrass": (199.5, 327.3),
    "East Port": (619.5, 329.9),
    "Midstein": (430.4, 379.8),
    "Fisherhus": (571.5, 405.1),
    "Aqueduct": (140.3, 449.8),
    "Reeds": (403.4, 460.3),
    "Helle": (29.6, 499.6),
    "Power Plant": (236.1, 490.0),
    "Waterfall": (569.8, 530.3),
    "Shipyard": (673.5, 539.9),
    "Holdhus": (89.7, 600.3),
    "Askehus": (260.5, 639.6),
    "Lumber Yard": (500.1, 620.4),
}


# How close the mouse must be to a named location to select it.
LOCATION_RADIUS = 28


# ============================================================
# LOAD MASK
# ============================================================

def load_mask(filename):
    """Load an 80x80 '#' / '.' road mask."""

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


# ============================================================
# LOAD HIGHWAY + WEAK NETWORK
# ============================================================

highway_cells = load_mask(HIGHWAY_MASK_FILE)
weak_cells = load_mask(WEAK_MASK_FILE)

road_cells = highway_cells | weak_cells


# ============================================================
# LOCATION ACCESS POINTS
# ============================================================
# Format:
#   "Location Name": (row, col)
#
# Empty at the beginning.
# The user will mark these manually.
# ============================================================

access_points = {}


# ============================================================
# STATE
# ============================================================

selected_location = None
message = "Click a named location, then click one of its road cells."


# ============================================================
# CONVERSIONS
# ============================================================

def location_to_screen(point):
    """Convert original-map pixels to displayed-map pixels."""

    x, y = point

    screen_x = int(
        x * WIDTH / MAP_ORIGINAL_WIDTH
    )

    screen_y = int(
        y * MAP_HEIGHT / MAP_ORIGINAL_HEIGHT
    )

    return screen_x, screen_y


def mouse_to_cell(position):
    """Convert mouse position into an 80x80 grid cell."""

    x, y = position

    if y >= MAP_HEIGHT:
        return None

    col = x // CELL_SIZE
    row = y // CELL_SIZE

    if 0 <= row < ROWS and 0 <= col < COLS:
        return row, col

    return None


def find_clicked_location(mouse_position):
    """Return the nearest named location if clicked closely enough."""

    mouse_x, mouse_y = mouse_position

    best_name = None
    best_distance = float("inf")

    for name, point in LOCATION_POINTS.items():

        location_x, location_y = location_to_screen(point)

        distance = (
            (mouse_x - location_x) ** 2
            + (mouse_y - location_y) ** 2
        ) ** 0.5

        if distance <= LOCATION_RADIUS and distance < best_distance:
            best_name = name
            best_distance = distance

    return best_name


# ============================================================
# SAVE ACCESS POINTS
# ============================================================

def save_access_points():
    """Save every assigned location as: name=row,col."""

    with open(ACCESS_FILE, "w", encoding="utf-8") as file:

        for name in LOCATION_POINTS:

            if name in access_points:
                row, col = access_points[name]
                file.write(f"{name}={row},{col}\n")

    print(f"Saved {ACCESS_FILE}")


def save_everything():
    """Save access points and the current screen."""

    save_access_points()

    screenshot_name = "Livik_80x80_Location_Access_Points.png"
    pygame.image.save(screen, screenshot_name)

    print(f"Saved screenshot as {screenshot_name}")


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(text, position, text_font, color=WHITE):
    surface = text_font.render(
        text,
        True,
        color
    )

    screen.blit(
        surface,
        position
    )


# ============================================================
# DRAW ROAD MASKS
# ============================================================

def draw_road_masks():

    # Highway cells
    for row, col in highway_cells:

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            HIGHWAY_COLOR,
            (
                x + 1,
                y + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
        )

    # Weak / muddy cells
    for row, col in weak_cells:

        x = col * CELL_SIZE
        y = row * CELL_SIZE

        pygame.draw.rect(
            screen,
            WEAK_COLOR,
            (
                x + 1,
                y + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
        )


# ============================================================
# DRAW NAMED LOCATIONS
# ============================================================

def draw_locations():

    for name, point in LOCATION_POINTS.items():

        x, y = location_to_screen(point)

        # Original named-location reference point
        pygame.draw.circle(
            screen,
            LOCATION_COLOR,
            (x, y),
            4
        )

        # Highlight selected location
        if name == selected_location:

            pygame.draw.circle(
                screen,
                SELECTED_COLOR,
                (x, y),
                12,
                2
            )

        # Draw label
        label = small_font.render(
            name,
            True,
            WHITE
        )

        label_x = x + 6
        label_y = y - 9

        # Keep labels on screen
        if label_x + label.get_width() > WIDTH:
            label_x = x - label.get_width() - 6

        if label_y < 0:
            label_y = y + 6

        screen.blit(
            label,
            (label_x, label_y)
        )


# ============================================================
# DRAW ACCESS POINTS
# ============================================================

def draw_access_points():

    for name, (row, col) in access_points.items():

        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2

        # Cyan access-point cell
        pygame.draw.rect(
            screen,
            ACCESS_COLOR,
            (
                col * CELL_SIZE + 1,
                row * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            ),
            2
        )

        # Small center marker
        pygame.draw.circle(
            screen,
            ACCESS_COLOR,
            (x, y),
            3
        )


# ============================================================
# DRAW HUD
# ============================================================

def draw_hud():

    pygame.draw.rect(
        screen,
        HUD_COLOR,
        (
            0,
            MAP_HEIGHT,
            WIDTH,
            HUD_HEIGHT
        )
    )

    if selected_location is None:

        status = "SELECT LOCATION"

    else:

        if selected_location in access_points:

            row, col = access_points[selected_location]

            status = (
                f"{selected_location} -> assigned "
                f"(row {row}, col {col})"
            )

        else:

            status = (
                f"{selected_location} selected -> "
                "click a RED or ORANGE road cell"
            )

    draw_text(
        status,
        (10, MAP_HEIGHT + 7),
        small_font,
        ACCESS_COLOR if selected_location else WHITE
    )

    draw_text(
        "LEFT: select location / assign road cell   "
        "RIGHT: remove access point",
        (10, MAP_HEIGHT + 29),
        small_font,
        LIGHT_TEXT
    )

    draw_text(
        "S: save + screenshot   M: save   C: confirm location   ESC: quit",
        (10, MAP_HEIGHT + 48),
        small_font,
        LIGHT_TEXT
    )

    counter = small_font.render(
        f"Highway: {len(highway_cells)}   "
        f"Weak: {len(weak_cells)}   "
        f"Access: {len(access_points)}/{len(LOCATION_POINTS)}",
        True,
        WHITE
    )

    counter_rect = counter.get_rect(
        topright=(WIDTH - 10, MAP_HEIGHT + 7)
    )

    screen.blit(
        counter,
        counter_rect
    )


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

            # ------------------------------------------------
            # LEFT CLICK
            # ------------------------------------------------

            if event.button == 1:

                # First check whether a named location was clicked.
                location_name = find_clicked_location(event.pos)

                if location_name is not None:

                    selected_location = location_name

                    if selected_location in access_points:

                        row, col = access_points[selected_location]

                        message = (
                            f"{selected_location} already assigned "
                            f"to ({row}, {col}). "
                            "Click another road cell to replace it."
                        )

                    else:

                        message = (
                            f"{selected_location} selected. "
                            "Now click a red or orange road cell."
                        )

                    continue

                # If a location is selected, a left click on the
                # map attempts to assign an access point.
                if selected_location is not None:

                    cell = mouse_to_cell(event.pos)

                    if cell is None:
                        continue

                    # HARD RULE:
                    # Access points may ONLY be existing road cells.
                    if cell not in road_cells:

                        message = (
                            "INVALID: access point must be on "
                            "an existing highway or weak road cell."
                        )

                        continue

                    # Assign exact road cell.
                    access_points[selected_location] = cell

                    row, col = cell

                    message = (
                        f"{selected_location} assigned to "
                        f"({row}, {col})."
                    )

            # ------------------------------------------------
            # RIGHT CLICK
            # ------------------------------------------------

            elif event.button == 3:

                cell = mouse_to_cell(event.pos)

                if cell is None:
                    continue

                removed_location = None

                for name, access_cell in access_points.items():

                    if access_cell == cell:

                        removed_location = name
                        break

                if removed_location is not None:

                    del access_points[removed_location]

                    message = (
                        f"Removed access point for "
                        f"{removed_location}."
                    )

    # ========================================================
    # KEYBOARD
    # ========================================================

        elif event.type == pygame.KEYDOWN:

            # Save + screenshot
            if event.key == pygame.K_s:

                save_everything()

                message = (
                    f"Saved {len(access_points)} access points."
                )

            # Save only
            elif event.key == pygame.K_m:

                save_access_points()

                message = (
                    f"Saved {len(access_points)} access points."
                )

            # C = confirm/save current location access point
            elif event.key == pygame.K_c:

                if selected_location is None:

                    message = (
                        "No location selected. "
                        "Left-click a named location first."
                    )

                elif selected_location not in access_points:

                    message = (
                        f"{selected_location} has no access point yet. "
                        "Left-click a red or orange road cell first."
                    )

                else:

                    row, col = access_points[selected_location]

                    # Save immediately to disk.
                    save_access_points()

                    message = (
                        f"{selected_location} saved at "
                        f"({row}, {col}). "
                        "Click the next named location."
                    )

                    # IMPORTANT:
                    # C finishes this location and returns the tool
                    # to LOCATION-SELECTION mode.
                    selected_location = None

            # Escape
            elif event.key == pygame.K_ESCAPE:

                running = False

    # ========================================================
    # DRAW
    # ========================================================

    screen.blit(
        map_image,
        (0, 0)
    )

    # Entire road network is visible.
    draw_road_masks()

    # Cyan access points appear above the road masks.
    draw_access_points()

    # Named locations and labels.
    draw_locations()

    # HUD
    draw_hud()

    # Temporary message
    if message:

        message_surface = small_font.render(
            message,
            True,
            ERROR_COLOR if message.startswith("INVALID") else WHITE
        )

        screen.blit(
            message_surface,
            (
                10,
                MAP_HEIGHT - 22
            )
        )

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
