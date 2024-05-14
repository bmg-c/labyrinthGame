from enum import Enum
from random import shuffle
from typing import Self


class CellState(Enum):
    EMPTY = 1
    PATH = 2
    START = 3
    EXIT = 4


class Cell:
    def __init__(self, state: CellState, x: int, y: int):
        self.state: CellState = state
        self.x: int = x
        self.y: int = y
        self.visited: bool = False
        self.walls: dict[str, bool] = {"N": True, "S": True, "W": True, "E": True}

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

    def cell_next_to(self, x0, y0, x1, y1) -> bool:
        diff_x = abs(x0 - x1)
        diff_y = abs(y0 - y1)

        if diff_x + diff_y >= 2 or diff_x + diff_y == 0:
            return False
        return True

    def direction_to(self, nc: Self) -> str | None:
        if not self.cell_next_to(self.x, self.y, nc.x, nc.y):
            return None
        diff_x = self.x - nc.x
        diff_y = self.y - nc.y

        if diff_x == 0:
            if diff_y == 1:
                return "N"
            elif diff_y == -1:
                return "S"
            else:
                return None
        elif diff_x == -1:
            return "E"
        elif diff_x == 1:
            return "W"
        return None

    def __str__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __unicode__(self):
        return f"{self.state}({self.x}, {self.y})"

    def __repr__(self):
        return f"{self.state}({self.x}, {self.y})"


add_x = {"N": 0, "S": 0, "W": -1, "E": 1}
add_y = {"N": -1, "S": 1, "W": 0, "E": 0}
opposite = {"N": "S", "S": "N", "W": "E", "E": "W"}

GEN_ALGORITHMS = ["recursive_backtracking", "custom"]
SOLVING_ALGORITHMS = ["backtracking"]


class SizeException(Exception):
    name: str = "Ошибка валидации размера"
    pass


class MazeValidationException(Exception):
    name: str = "Ошибка валидации начальных данных лабиринта"
    pass


class AlgorithmException(Exception):
    name: str = "Ошибка валидации алгоритма"
    pass


class SolvingException(Exception):
    name: str = "Ошибка при решении лабиринта"
    pass


class ArgumentsException(Exception):
    name: str = "Ошибка валидации аргументов функции"
    pass


class Maze:
    is_solvable: bool
    start_cell: Cell
    exit_cell: Cell

    def __init__(self, num_rows: int = 0, num_cols: int = 0, gen_algorithm: str = "recursive_backtracking", solving_algorithm: str = "backtracking",
                 custom_grid: list[list[Cell]] | None = None):
        self.check_input_data(num_rows, num_cols, gen_algorithm, solving_algorithm, custom_grid)

        if custom_grid is None:
            self.num_rows: int = num_rows
            self.num_cols: int = num_cols

            self.grid: list[list[Cell]] = self.generate_grid()
            self.generate_maze(gen_algorithm)
            self.start_cell: Cell = self.get_start_cell()
            self.exit_cell: Cell = self.get_exit_cell()

            self.path: list[Cell] = []
            self.solve(solving_algorithm)
            if not self.is_solvable or len(self.path) == 0:
                raise SolvingException("Лабиринт не имеет решения. Лабиринт должен иметь путь от начала до конца")
        elif custom_grid is not None:
            self.num_rows: int = len(custom_grid)
            self.num_cols: int = len(custom_grid[0])

            self.grid: list[list[Cell]] = custom_grid.copy()
            self.start_cell: Cell = self.get_start_cell()
            self.exit_cell: Cell = self.get_exit_cell()

            self.path: list[Cell] = []
            self.solve(solving_algorithm)
            if not self.is_solvable or len(self.path) == 0:
                raise SolvingException("Лабиринт не имеет решения. Лабиринт должен иметь путь от начала до конца")
        else:
            raise ArgumentsException("Приведено недостаточно аргументов")

    def check_input_data(self, num_rows: int, num_cols: int, gen_algorithm: str, solving_algorithm: str,
                         custom_grid: list[list[Cell]] | None) -> None:
        if custom_grid is not None:
            num_rows = len(custom_grid)
            if num_rows == 0:
                raise SizeException("Размер лабиринта не может быть меньше 2")
            num_cols = len(custom_grid[0])

            for y in range(num_rows):
                for x in range(num_cols):
                    if (x, y) != (custom_grid[y][x].x, custom_grid[y][x].y):
                        raise MazeValidationException(
                            "Координаты клеток внутри самих клеток не сходятся с их расположением в лабиринте")

            gen_algorithm = "custom"
        if num_rows < 2 or num_cols < 2:
            raise SizeException("Размер лабиринта не может быть меньше 2")
        if num_rows > 30 or num_cols > 30:
            raise SizeException("Размер лабиринта не может быть больше 30")
        if gen_algorithm not in GEN_ALGORITHMS:
            raise AlgorithmException("Такого алгоритма генерации лабиринта не существует")
        if solving_algorithm not in SOLVING_ALGORITHMS:
            raise AlgorithmException("Такого алгоритма нахождения пути в лабиринте не существует")
        return None

    def get_start_cell(self) -> Cell:
        grid = self.grid
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x].state == CellState.START:
                    return grid[y][x]
        grid[0][0].state = CellState.START
        return grid[0][0]

    def get_exit_cell(self) -> Cell:
        grid = self.grid
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x].state == CellState.EXIT:
                    return grid[y][x]
        grid[-1][-1].state = CellState.EXIT
        return grid[-1][-1]

    def generate_grid(self) -> list[list[Cell]]:
        grid: list[list[Cell]] = []

        for y in range(self.num_rows):
            grid.append(list())
            for x in range(self.num_cols):
                grid[y].append(Cell(CellState.EMPTY, x, y))

        return grid

    def clear_visited(self) -> None:
        for y in range(self.num_rows):
            for x in range(self.num_cols):
                self.grid[y][x].visited = False

    def get_cell_available_directions(self, cc: Cell) -> list[str]:
        wall_directions = cc.get_available_directions()
        directions = []

        for direction in wall_directions:
            if not self.grid[cc.y + add_y[direction]][cc.x + add_x[direction]].visited:
                directions.append(direction)

        return directions

    def generate_maze(self, algorithm: str) -> None:
        if algorithm == "recursive_backtracking":
            self._recursive_backtracking_method(0, 0, self.grid)

    def _recursive_backtracking_method(self, cx: int, cy: int, grid: list[list[Cell]]) -> None:
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

    def solve(self, algorithm: str) -> None:
        if algorithm == "backtracking":
            answer = self._solve_backtracking()
            self.is_solvable = answer[0]
            self.path = answer[1]
        else:
            raise AlgorithmException("Такого алгоритма нахождения пути в лабиринте не существует")

    def _solve_backtracking(self) -> (bool, list[Cell]):
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
            cx, cy = nc.x, nc.y

        return False, []
