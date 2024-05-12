import unittest
from maze import Maze, SizeException, SolvingException, MazeValidationException, AlgorithmException, ArgumentsException, Cell, CellState, cell_next_to


class TestCellLogic(unittest.TestCase):
    def test_cell_next_to(self):
        cell1 = Cell(CellState.EMPTY, 0, 0)
        cell2 = Cell(CellState.EMPTY, 0, 1)
        cell3 = Cell(CellState.EMPTY, 1, 0)
        cell4 = Cell(CellState.EMPTY, 1, 1)

        self.assertTrue(cell_next_to(cell1.x, cell1.y, cell2.x, cell2.y))
        self.assertTrue(cell_next_to(cell1.x, cell1.y, cell3.x, cell3.y))
        self.assertFalse(cell_next_to(cell1.x, cell1.y, cell4.x, cell4.y))

        self.assertFalse(cell_next_to(cell2.x, cell2.y, cell3.x, cell3.y))
        self.assertTrue(cell_next_to(cell2.x, cell2.y, cell4.x, cell4.y))

        self.assertTrue(cell_next_to(cell3.x, cell3.y, cell4.x, cell4.y))

    def test_direction_to(self):
        cell1 = Cell(CellState.EMPTY, 0, 0)
        cell1.walls = {"N": True, "S": False, "W": True, "E": False}
        cell2 = Cell(CellState.EMPTY, 0, 1)
        cell2.walls = {"N": False, "S": True, "W": True, "E": False}
        cell3 = Cell(CellState.EMPTY, 1, 0)
        cell2.walls = {"N": True, "S": True, "W": False, "E": True}
        cell4 = Cell(CellState.EMPTY, 1, 1)
        cell2.walls = {"N": True, "S": True, "W": False, "E": True}

        self.assertEqual(cell1.direction_to(cell2), "S")
        self.assertEqual(cell2.direction_to(cell1), "N")

        self.assertEqual(cell1.direction_to(cell3), "E")
        self.assertEqual(cell3.direction_to(cell1), "W")

        self.assertEqual(cell2.direction_to(cell4), "E")
        self.assertEqual(cell4.direction_to(cell2), "W")

        self.assertEqual(cell1.direction_to(cell4), None)
        self.assertEqual(cell4.direction_to(cell1), None)

        self.assertEqual(cell2.direction_to(cell3), None)
        self.assertEqual(cell3.direction_to(cell2), None)


class TestMazeRandom(unittest.TestCase):
    def setUp(self):
        self.init_size = 10
        self.maze: Maze = Maze(num_rows=self.init_size, num_cols=self.init_size)

    def test_null(self):
        self.assertIsNotNone(self.maze)
        self.assertIsNotNone(self.maze.grid)
        self.assertIsNotNone(self.maze.start_cell)
        self.assertIsNotNone(self.maze.exit_cell)
        self.assertIsNotNone(self.maze.path)

    def test_size(self):
        self.assertTrue(self.init_size == self.maze.num_cols == len(self.maze.grid))
        self.assertTrue(self.init_size == self.maze.num_rows == len(self.maze.grid[0]))

    def test_respective_positions(self):
        start_cells: list[Cell] = []
        exit_cells: list[Cell] = []
        for y in range(self.maze.num_rows):
            for x in range(self.maze.num_cols):
                cell = self.maze.grid[y][x]
                if cell.state == CellState.START:
                    start_cells.append(cell)
                if cell.state == CellState.EXIT:
                    exit_cells.append(cell)
        # No more than one of each start cell and exit cell
        self.assertEqual(1, len(start_cells))
        self.assertEqual(1, len(exit_cells))
        # Start cell and exit cell in their respective places
        self.assertEqual(self.maze.start_cell, start_cells[0])
        self.assertEqual(self.maze.exit_cell, exit_cells[0])

    def test_solved_path(self):
        # Size of path can't be less than initial maze size
        self.assertGreaterEqual(len(self.maze.path), self.init_size)
        # First element should be next to start cell and not a behind wall
        self.assertTrue(cell_next_to(self.maze.start_cell.x, self.maze.start_cell.y, self.maze.path[0].x, self.maze.path[0].y))
        self.assertIsNotNone(self.maze.start_cell.direction_to(self.maze.path[0]))
        # Last element should be next to exit cell and not behind wall
        self.assertTrue(cell_next_to(self.maze.exit_cell.x, self.maze.exit_cell.y, self.maze.path[-1].x, self.maze.path[-1].y))
        self.assertIsNotNone(self.maze.exit_cell.direction_to(self.maze.path[-1]))
        for i in range(0, len(self.maze.path) - 1):
            # Elements should not repeat in path
            self.assertTrue(self.maze.path[i] not in self.maze.path[0:i])
            # Elements should be next to each other and not behind wall
            self.assertTrue(cell_next_to(self.maze.path[i].x, self.maze.path[i].y, self.maze.path[i+1].x, self.maze.path[i+1].y))
            self.assertIsNotNone(self.maze.path[i].direction_to(self.maze.path[i+1]))


if __name__ == "__main__":
    unittest.main()
