import time
import random
import tkinter as tk
import sys
import pygame

def create_grid(rows, cols):
    """Create a grid with random initial states."""
    return [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]

def count_live_neighbors(grid, row, col):
    """Count the number of live neighbors for a cell."""
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),          (0, 1),
        (1, -1), (1, 0), (1, 1),
    ]
    count = 0
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            count += grid[r][c]
    return count

def next_generation(grid):
    """Compute the next generation of the grid."""
    rows, cols = len(grid), len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            live_neighbors = count_live_neighbors(grid, r, c)
            if grid[r][c] == 1 and live_neighbors in (2, 3):
                new_grid[r][c] = 1
            elif grid[r][c] == 0 and live_neighbors == 3:
                new_grid[r][c] = 1
    return new_grid

def draw_pattern_in_window(grid, cell_size):
    """
    Allows the user to draw a pattern in the window by clicking cells.
    """
    pygame.init()
    rows, cols = len(grid), len(grid[0])
    screen = pygame.display.set_mode((cols * cell_size, rows * cell_size))
    pygame.display.set_caption("Draw Your Pattern - Conway's Game of Life")
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear the screen

        # Draw the grid
        for x in range(rows):
            for y in range(cols):
                color = (255, 255, 255) if grid[x][y] == 1 else (0, 0, 0)
                pygame.draw.rect(screen, color, (y * cell_size, x * cell_size, cell_size, cell_size))
                pygame.draw.rect(screen, (50, 50, 50), (y * cell_size, x * cell_size, cell_size, cell_size), 1)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                grid_y, grid_x = y // cell_size, x // cell_size  # Corrected the order of grid_x and grid_y
                grid[grid_y][grid_x] = 1 - grid[grid_y][grid_x]  # Toggle cell state
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to finish drawing
                    running = False

        clock.tick(30)

    pygame.quit()

def draw_pattern_with_tkinter(grid, cell_size):
    """
    Allows the user to draw a pattern using a tkinter Canvas.
    """
    rows, cols = len(grid), len(grid[0])
    root = tk.Tk()
    root.title("Draw Your Pattern - Conway's Game of Life")
    canvas = tk.Canvas(root, width=cols * cell_size, height=rows * cell_size, bg="white")
    canvas.pack()

    drawing = False  # Track if the mouse button is held down

    def toggle_cell(event):
        x, y = event.x // cell_size, event.y // cell_size
        if 0 <= y < rows and 0 <= x < cols:
            grid[y][x] = 1 - grid[y][x]  # Toggle cell state
            color = "black" if grid[y][x] == 1 else "white"
            canvas.create_rectangle(x * cell_size, y * cell_size, 
                                    (x + 1) * cell_size, (y + 1) * cell_size, 
                                    fill=color, outline="gray")

    def start_drawing(event):
        nonlocal drawing
        drawing = True
        toggle_cell(event)

    def stop_drawing(event):
        nonlocal drawing
        drawing = False

    def draw_on_drag(event):
        x, y = event.x // cell_size, event.y // cell_size
        if 0 <= y < rows and 0 <= x < cols and grid[y][x] == 0:  # Only redraw if the state changes
            toggle_cell(event)

    def draw_grid():
        for x in range(cols):
            for y in range(rows):
                color = "black" if grid[y][x] == 1 else "white"
                canvas.create_rectangle(x * cell_size, y * cell_size, 
                                        (x + 1) * cell_size, (y + 1) * cell_size, 
                                        fill=color, outline="gray")

    def start_simulation():
        # Advance the simulation by one frame to display the initial drawing
        nonlocal grid  # Use the grid from the outer scope
        grid = next_generation(grid)  # Advance the grid by one generation
        root.destroy()  # Exit the drawing phase

    canvas.bind("<Button-1>", start_drawing)
    canvas.bind("<B1-Motion>", draw_on_drag)
    canvas.bind("<ButtonRelease-1>", stop_drawing)
    draw_grid()
    start_button = tk.Button(root, text="Start Simulation", command=start_simulation)
    start_button.pack()
    root.mainloop()

class GameOfLifeApp:
    def __init__(self, root, rows, cols, cell_size=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid = create_grid(rows, cols)
        self.canvas = tk.Canvas(root, width=cols * cell_size, height=rows * cell_size, bg="white")
        self.canvas.pack()
        self.running = True
        self.paused = True  # Start the simulation in a paused state
        self.history = []  # To store previous generations for stepping backward
        # Add buttons for controls
        self.control_frame = tk.Frame(root)
        self.control_frame.pack()
        self.play_button = tk.Button(self.control_frame, text="Play", command=self.play)
        self.play_button.pack(side=tk.LEFT)
        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause)
        self.pause_button.pack(side=tk.LEFT)
        self.step_forward_button = tk.Button(self.control_frame, text="Step Forward", command=self.step_forward)
        self.step_forward_button.pack(side=tk.LEFT)
        self.step_backward_button = tk.Button(self.control_frame, text="Step Backward", command=self.step_backward)
        self.step_backward_button.pack(side=tk.LEFT)
        self.root.after(0, self.update)

    def play(self):
        """Start the simulation."""
        self.paused = False

    def pause(self):
        """Pause the simulation."""
        self.paused = True

    def step_forward(self):
        """Step forward one generation."""
        if self.paused:
            self.history.append([row[:] for row in self.grid])  # Save current state
            self.grid = next_generation(self.grid)
            self.draw_grid()

    def step_backward(self):
        """Step backward one generation."""
        if self.paused and self.history:
            self.grid = self.history.pop()  # Restore the last saved state
            self.draw_grid()

    def draw_grid(self):
        """Draw the grid on the canvas."""
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                if self.grid[r][c] == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

    def update(self):
        """Update the grid and redraw it."""
        if not self.paused:
            self.history.append([row[:] for row in self.grid])  # Save current state
            self.grid = next_generation(self.grid)
            self.draw_grid()
        self.root.after(200, self.update)

def main():
    """Main function to run the Game of Life."""
    try:
        print("Specify the size of the grid:")
        rows = int(input("Enter the number of rows: "))
        cols = int(input("Enter the number of columns: "))
    except ValueError:
        print("Invalid input. Please enter integers for rows and columns.")
        sys.exit(1)

    cell_size = 20  # Size of each cell in pixels
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    print("Draw your initial pattern in the window. Click 'Start Simulation' when done.")
    draw_pattern_with_tkinter(grid, cell_size)  # Wait for the user to finish drawing
    # Start the simulation only after the user finishes drawing
    root = tk.Tk()
    root.title("Game of Life")
    app = GameOfLifeApp(root, rows, cols, cell_size)
    app.grid = grid  # Use the grid drawn by the user
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nGame interrupted. Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()