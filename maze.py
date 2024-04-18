from enum import Enum
from random import shuffle

def cell_next_to(x0, y0, x1, y1):
    diff_x = abs(x0 - x1)
    diff_y = abs(y0 - y1)

    if diff_x + diff_y >= 2 or diff_x + diff_y == 0:
        return False
    return True

class CellState(Enum):
    EMPTY = 1
    PATH = 2
    START = 3
    EXIT = 4


class Cell:
    def __init__(self, state: CellState, x: int, y: int):
        self.state = state
        self.x = x
        self.y = y
        self.visited = False
        self.walls = {"N": True, "S": True, "W": True, "E": True}

    def get_available_directions(self) -> list[str]:
        directions: list[str] = []
        if not self.walls["N"]:
            directions.append("N")
        if not self.walls["S"]:
            directions.append("S")
        if not self.walls["W"]:
            directions.append("W")
        if not self.walls["E"]:
            directions.append("E")
        return directions

    def direction_to(self, nc) -> str:
        if cell_next_to(self.x, self.y, nc.x, nc.y):
            return "None"
        diff_x = self.x - nc.x
        diff_y = self.y - nc.y

        if diff_x == 0:
            if diff_y == 1:
                return "N"
            elif diff_y == -1:
                return "S"
            else:
                return "Same"
        elif diff_x == -1:
            return "E"
        elif diff_x == 1:
            return "W"
        return "Error"

    def __str__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __unicode__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __repr__(self):
        return f"{self.state}({self.x}, {self.y})"


add_x = {"N": 0, "S": 0, "W": -1, "E": 1}
add_y = {"N": -1, "S": 1, "W": 0, "E": 0}
opposite = {"N": "S", "S": "N", "W": "E", "E": "W"}


class Maze:
    def __init__(self, num_rows: int, num_cols: int, algorithm: str = "recursive_backtracking"):
        self.num_rows = num_rows
        self.num_cols = num_cols
        grid = self.generate_grid()
        self.grid_size = num_rows * num_cols
        self.grid: list[list[Cell]] = self.generate_maze(grid, algorithm)
        self.start_cell = grid[0][0]
        self.exit_cell = grid[num_rows - 1][num_cols - 1]

        self.is_solvable = False
        self.path = []
        self.solve("recursive_backtracking")

    def generate_grid(self) -> list[list[Cell]]:
        grid: list[list[Cell]] = []

        for y in range(self.num_rows):
            grid.append(list())
            for x in range(self.num_cols):
                grid[y].append(Cell(CellState.EMPTY, x, y))

        return grid

    def clear_visited(self):
        for y in range(self.num_rows):
            for x in range(self.num_cols):
                self.grid[y][x].visited = False

    def get_cell_available_directions(self, cc):
        wall_directions = cc.get_available_directions()
        directions = []
        print(f"({cc.y}, {cc.x}) - {wall_directions}")

        for direction in wall_directions:
            if not self.grid[cc.y + add_y[direction]][cc.x + add_x[direction]].visited:
                directions.append(direction)

        return directions

    def generate_maze(self, grid, algorithm) -> list[list[Cell]]:
        if algorithm == "recursive_backtracking":
            self._recursive_backtracking_method(0, 0, grid)
            return grid
        return grid

    def _recursive_backtracking_method(self, cx, cy, grid):
        grid[cy][cx].visited = True

        directions: list[str] = ["N", "S", "W", "E"]
        shuffle(directions)

        for direction in directions:
            nx, ny = cx + add_x[direction], cy + add_y[direction]

            if (0 <= ny <= self.num_rows - 1) and (0 <= nx <= self.num_cols - 1) and not grid[ny][nx].visited:
                grid[cy][cx].walls[direction] = False
                grid[ny][nx].walls[opposite[direction]] = False
                grid[ny][nx].visited = True

                self._recursive_backtracking_method(nx, ny, grid)

    def print_maze(self):
        char_grid = []
        for x in range(self.num_rows * 2 + 1):
            char_grid.append([])
            for y in range(self.num_cols * 2 + 1):
                char_grid[x].append('⬛')

        for y in range(len(char_grid)):
            for x in range(len(char_grid[0])):
                if x % 2 == 1 and y % 2 == 1:
                    char_grid[y][x] = '⬜'
                    cellx, celly = int((x - 1) / 2), int((y - 1) / 2)  # 0,0-1,1  0,1-1,3  0,2-1,5
                    if not self.grid[celly][cellx].walls["N"]:
                        char_grid[y - 1][x] = '⬜'
                    if not self.grid[celly][cellx].walls["S"]:
                        char_grid[y + 1][x] = '⬜'
                    if not self.grid[celly][cellx].walls["W"]:
                        char_grid[y][x - 1] = '⬜'
                    if not self.grid[celly][cellx].walls["E"]:
                        char_grid[y][x + 1] = '⬜'

        for x in range(len(char_grid)):
            for y in range(len(char_grid[0])):
                print(char_grid[x][y], end='')
            print()

    def solve(self, algorithm: str):
        if algorithm == "recursive_backtracking":
            answer = self._solve_recursive_backtracking()
            self.is_solvable = answer[0]
            self.path = answer[1]
        else:
            print("No such solving algorithm")

    def _solve_recursive_backtracking(self) -> (bool, list[Cell]):
        self.clear_visited()
        cx, cy = self.start_cell.x, self.start_cell.y
        stack: list[Cell] = [self.grid[cy][cx]]

        while True:
            self.grid[cy][cx].visited = True
            if self.grid[cy][cx] is not stack[-1]:
                stack.append(self.grid[cy][cx])
            if self.grid[cy][cx] is self.exit_cell:
                return True, stack[1:-1]

            directions = self.get_cell_available_directions(self.grid[cy][cx])
            if len(directions) == 0:
                if self.grid[cy][cx] is self.start_cell:
                    break
                stack.pop()
                cc = stack[-1]
                cx, cy = cc.x, cc.y
                continue
            shuffle(directions)

            direction = directions.pop()
            nc = self.grid[cy + add_y[direction]][cx + add_x[direction]]
            print(f"({cy}, {cx}) - ({nc.y}, {nc.x}) / {direction}")
            cx, cy = nc.x, nc.y

        return False, []


new_maze = Maze(5, 5)
new_maze.print_maze()
print("Is solvable? " + str(new_maze.is_solvable))
print("Path: " + str(new_maze.path))
