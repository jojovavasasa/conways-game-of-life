import time
import random
import tkinter as tk

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
        self.root.after(0, self.update)

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
        if self.running:
            self.grid = next_generation(self.grid)
            self.draw_grid()
            self.root.after(200, self.update)

def main():
    """Main function to run the Game of Life."""
    rows, cols = 50, 50  # Adjust grid size as needed
    cell_size = 10       # Size of each cell in pixels

    root = tk.Tk()
    root.title("Game of Life")
    app = GameOfLifeApp(root, rows, cols, cell_size)
    root.mainloop()

if __name__ == "__main__":
    main()
