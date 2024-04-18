from enum import Enum
from random import shuffle


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

    def generate_grid(self) -> list[list[Cell]]:
        grid: list[list[Cell]] = []

        for i in range(self.num_rows):
            grid.append(list())
            for j in range(self.num_cols):
                grid[i].append(Cell(CellState.EMPTY, i, j))

        return grid

    def clear_visited(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.grid[i][j].visited = False

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

    def is_solvable(self) -> bool:
        self.clear_visited()
        self._solved = False
        self._is_solvable(self.start_cell.x, self.start_cell.y, self.grid)
        return self._solved

    def _is_solvable(self, cx, cy, grid: list[list[Cell]]):
        grid[cy][cx].visited = True

        directions: list[str] = grid[cy][cx].get_available_directions()
        shuffle(directions)
        # print(str(directions) + f" [{self.grid[cy][cx].x}, {self.grid[cy][cx].y}]")

        if cx == self.exit_cell.x and cy == self.exit_cell.y:
            self._solved = True

        for direction in directions:
            nx, ny = cx + add_x[direction], cy + add_y[direction]

            if (0 <= ny <= self.num_rows - 1) and (0 <= nx <= self.num_cols - 1) and not grid[ny][nx].visited:
                grid[ny][nx].visited = True

                self._is_solvable(nx, ny, grid)


new_maze = Maze(5, 5)
new_maze.print_maze()
print("Is solvable? " + str(new_maze.is_solvable()))
