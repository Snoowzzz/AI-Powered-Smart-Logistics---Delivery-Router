# AI Smart Logistics Router — Progress Note

## Current Status
**Milestone 1 complete: Pygame grid application is working.**

### Setup completed
- Created GitHub repository
- Linked GitHub with VS Code
- Installed Pygame successfully
- Created `app.py`

### What we built
- 800×800 Pygame window
- 20×20 city grid
- Each cell is 40×40 pixels
- Mouse clicks convert screen coordinates to `(row, col)`
- Clicked cells are stored in a `set`
- Clicked cells become blocked/gray
- Basic Pygame event loop and 60 FPS refresh

### Concepts understood
- `pygame.init()`
- Pygame window creation
- `while running` game loop
- Event handling
- Nested loops for drawing the grid
- Screen coordinates → grid coordinates
- Using a `set` for blocked cells

## Next Step
**Do not jump to A* yet.**

Next: add the ability to place:
- Depot / Start
- Delivery / Goal
- Obstacles

Then move toward A* pathfinding.

## Current file
`app.py`

## Run
```powershell
python app.py
```
