from customtkinter import *
import pickle
from .common import Block, BlockState, constants
from .maze import Cell, Maze, SizeException, SolvingException, MazeValidationException, AlgorithmException, \
    ArgumentsException
from tkinter import filedialog, Event
from CTkMessagebox import CTkMessagebox


class MazeBuilderWindow(CTkToplevel):
    filepath: str = ""
    upper_panel: CTkFrame
    control_bar: CTkFrame
    size_str: StringVar
    maze_width: int
    maze_height: int
    lowest_size: int
    block_width: int
    block_height: int
    canvas: CTkCanvas
    canvas_blocks: list[list[Block]] = []

    def __init__(self, master: CTk):
        super().__init__(master)

        self.title("Maze Builder")
        self.geometry("750x800")
        self.columnconfigure(0, weight=1, uniform="group2")
        self.rowconfigure(2, weight=1, uniform="group3")
        self.resizable(False, False)

        self.init_upper_panel()
        self.init_control_bar()

    def init_upper_panel(self) -> None:
        self.upper_panel = CTkFrame(self)
        self.upper_panel.grid(row=0, column=0, sticky="new")
        self.upper_panel.grid_columnconfigure((0, 1), weight=1)
        self.upper_panel.grid_rowconfigure(0, weight=1)

        title_label = CTkLabel(self.upper_panel, text="Построитель лабиринтов")
        title_label.grid(row=0, column=0, sticky="n")
        exit_button = CTkButton(self.upper_panel, text="Закрыть", command=self.destroy)
        exit_button.grid(row=0, column=1, sticky="ne")

    def init_control_bar(self) -> None:
        self.control_bar = CTkFrame(self)
        self.control_bar.grid(row=1, column=0, sticky="new")
        self.control_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.control_bar.grid_rowconfigure(0, weight=1)

        self.size_str = StringVar()
        self.size_str.set("5")
        size_entry = CTkEntry(self.control_bar, textvariable=self.size_str)
        size_entry.configure(validate='all', validatecommand=(self.register(self.size_validate), '%P'))
        size_entry.grid(row=0, column=0, sticky="nse")
        size_button = CTkButton(self.control_bar, text="Поставить размер", command=self.set_new_size)
        size_button.grid(row=0, column=1, sticky="nsw")

        save_button = CTkButton(self.control_bar, text="Экспорт", command=self.save_to_file)
        save_button.grid(row=0, column=2, sticky="nse")
        load_button = CTkButton(self.control_bar, text="Импорт", command=self.load_from_file)
        load_button.grid(row=0, column=3, sticky="nsw")

    def set_new_size(self) -> None:
        size = self.size_str.get()
        if size == "":
            return
        num_cols = int(size)
        num_rows = int(size)
        self.maze_width = num_cols * 2 + 1
        self.maze_height = num_rows * 2 + 1

        if num_rows < 2:
            self.handle_error(SizeException("Rазмер лабиринта не может быть меньше 2"))
            return
        if num_cols < 2:
            self.handle_error(SizeException("Rазмер лабиринта не может быть меньше 2"))
            return
        if num_rows != num_cols:
            self.handle_error(SizeException("Rазмер лабиринта по ширине и длине должен быть равен"))
            return

        self.init_canvas()

    def update_widget_size(self) -> None:
        self.master.update()
        widget_width = self.winfo_width()
        widget_height = self.winfo_height() - self.upper_panel.winfo_height() - self.control_bar.winfo_height()
        self.lowest_size = widget_width if widget_width < widget_height else widget_height

    def is_block_changeable(self, block: Block) -> (bool, BlockState):
        if block.x == 0 or block.y == 0:
            return False, BlockState.WALL
        if block.x == self.maze_width - 1 or block.y == self.maze_height - 1:
            return False, BlockState.WALL
        if block.x % 2 == 0 and block.y % 2 == 0:
            return False, BlockState.WALL
        if block.x % 2 == 1 and block.y % 2 == 1:
            return False, BlockState.EMPTY
        return True, block.state

    def init_canvas(self) -> None:
        self.update_widget_size()
        self.block_width = int(self.lowest_size / self.maze_width)
        self.block_height = int(self.lowest_size / self.maze_height)
        canvas_width = self.block_width * self.maze_width
        canvas_height = self.block_height * self.maze_height
        self.canvas = CTkCanvas(self, width=canvas_width, height=canvas_height)
        self.canvas.grid(row=2, column=0, sticky="news")
        self.canvas.bind("<B1-Motion>", self.left_click_event)
        self.canvas.bind("<Button-1>", self.left_click_event)
        self.canvas.bind("<B3-Motion>", self.right_click_event)
        self.canvas.bind("<Button-3>", self.right_click_event)

        self.canvas_blocks: list[list[Block]] = []
        for y in range(self.maze_height):
            self.canvas_blocks.append([])
            for x in range(self.maze_width):
                self.canvas_blocks[y].append(Block(x, y, BlockState.EMPTY))

        for y in range(self.maze_height):
            for x in range(self.maze_width):
                is_block_changeable, state = self.is_block_changeable(self.canvas_blocks[y][x])
                if not is_block_changeable:
                    self.canvas_blocks[y][x].state = state
                else:
                    self.canvas_blocks[y][x].state = BlockState.WALL

        self.canvas_blocks[1][1].state = BlockState.START
        self.canvas_blocks[-2][-2].state = BlockState.EXIT

        for y in range(0, self.maze_height):
            for x in range(0, self.maze_width):
                args = [
                    x * self.block_width,
                    y * self.block_height,
                    (x + 1) * self.block_width,
                    (y + 1) * self.block_height,
                ]
                kwargs = {}
                match self.canvas_blocks[y][x].state:
                    case BlockState.WALL:
                        kwargs["fill"] = constants["WALL_COLOR"]
                    case BlockState.PATH:
                        kwargs["fill"] = constants["PATH_COLOR"]
                    case BlockState.EMPTY:
                        kwargs["fill"] = constants["EMPTY_COLOR"]
                        kwargs["outline"] = constants["EMPTY_COLOR"]
                    case BlockState.START:
                        kwargs["fill"] = constants["START_COLOR"]
                    case BlockState.EXIT:
                        kwargs["fill"] = constants["EXIT_COLOR"]
                    case _:
                        print("Error defining color!")

                self.canvas_blocks[y][x].rectangle = self.canvas.create_rectangle(*args, **kwargs)

    def reset_canvas_blocks(self) -> None:
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                self.canvas_blocks[y][x].state = BlockState.WALL
                self.canvas.itemconfig(self.canvas_blocks[y][x].rectangle, fill=constants[BlockState.WALL.to_color()],
                                       outline=constants[BlockState.WALL.to_color()])

        for y in range(self.maze_height):
            for x in range(self.maze_width):
                is_block_changeable, state = self.is_block_changeable(self.canvas_blocks[y][x])
                if not is_block_changeable:
                    self.canvas_blocks[y][x].state = state
                    self.canvas.itemconfig(self.canvas_blocks[y][x].rectangle, fill=constants[state.to_color()],
                                           outline=constants[state.to_color()])
                else:
                    self.canvas_blocks[y][x].state = BlockState.WALL
                    self.canvas.itemconfig(self.canvas_blocks[y][x].rectangle,
                                           fill=constants[BlockState.WALL.to_color()],
                                           outline=constants[BlockState.WALL.to_color()])

    def left_click_event(self, event: Event) -> None:
        if self.canvas is None:
            return
        block_x = int(event.x / self.block_width)
        block_y = int(event.y / self.block_height)
        clicked_block = self.canvas_blocks[block_y][block_x]

        if self.is_block_changeable(clicked_block)[0]:
            clicked_block.state = BlockState.EMPTY
            self.canvas.itemconfig(clicked_block.rectangle, fill=constants[BlockState.EMPTY.to_color()],
                                   outline=constants[BlockState.EMPTY.to_color()])

    def right_click_event(self, event: Event) -> None:
        if self.canvas is None:
            return
        block_x = int(event.x / self.block_width)
        block_y = int(event.y / self.block_height)
        clicked_block = self.canvas_blocks[block_y][block_x]

        if self.is_block_changeable(clicked_block)[0]:
            clicked_block.state = BlockState.WALL
            self.canvas.itemconfig(clicked_block.rectangle, fill=constants[BlockState.WALL.to_color()],
                                   outline=constants[BlockState.WALL.to_color()])

    def save_to_file(self) -> None:
        cells = self.canvas_blocks_to_cell_matrix()
        try:
            maze = Maze(custom_grid=cells)
        except Exception as e:
            self.handle_error(e)
            return
        file = filedialog.asksaveasfile()
        filepath = file.name
        filehandler = open(filepath, 'wb')
        pickle.dump(cells, filehandler, pickle.HIGHEST_PROTOCOL)

    def load_from_file(self) -> None:
        try:
            filepath = filedialog.askopenfile()
            filepath = filepath.name
            filehandler = open(filepath, 'rb')
            cells: list[list[Cell]] = pickle.load(filehandler)
        except:
            CTkMessagebox(icon="cancel", title="Ошибка импортирования лабиринта", message="Ошибка при чтении файла")
            return

        num_rows = len(cells)
        if num_rows < 2:
            self.handle_error(SizeException("Rазмер лабиринта не может быть меньше 2"))
            return
        num_cols = len(cells[0])
        if num_cols < 2:
            self.handle_error(SizeException("Rазмер лабиринта не может быть меньше 2"))
            return
        if num_rows != num_cols:
            self.handle_error(SizeException("Rазмер лабиринта по ширине и длине должен быть равен"))
            return

        self.size_str.set(str(num_cols))
        self.set_new_size()

        for cy in range(num_rows):
            for cx in range(num_cols):
                bx, by = cx * 2 + 1, cy * 2 + 1
                if not cells[cy][cx].walls["N"]:
                    self.canvas_blocks[by - 1][bx].state = BlockState.EMPTY
                    self.canvas.itemconfig(self.canvas_blocks[by - 1][bx].rectangle,
                                           fill=constants[BlockState.EMPTY.to_color()],
                                           outline=constants[BlockState.EMPTY.to_color()])
                if not cells[cy][cx].walls["S"]:
                    self.canvas_blocks[by + 1][bx].state = BlockState.EMPTY
                    self.canvas.itemconfig(self.canvas_blocks[by + 1][bx].rectangle,
                                           fill=constants[BlockState.EMPTY.to_color()],
                                           outline=constants[BlockState.EMPTY.to_color()])
                if not cells[cy][cx].walls["W"]:
                    self.canvas_blocks[by][bx - 1].state = BlockState.EMPTY
                    self.canvas.itemconfig(self.canvas_blocks[by][bx - 1].rectangle,
                                           fill=constants[BlockState.EMPTY.to_color()],
                                           outline=constants[BlockState.EMPTY.to_color()])
                if not cells[cy][cx].walls["E"]:
                    self.canvas_blocks[by][bx + 1].state = BlockState.EMPTY
                    self.canvas.itemconfig(self.canvas_blocks[by][bx + 1].rectangle,
                                           fill=constants[BlockState.EMPTY.to_color()],
                                           outline=constants[BlockState.EMPTY.to_color()])

    def size_validate(self, value: str) -> bool:
        size: str = value
        if size == "":
            return True
        if not size.isnumeric():
            return False
        return True

    def canvas_blocks_to_cell_matrix(self) -> list[list[Cell]]:
        blocks = self.canvas_blocks

        maze_height = int((len(blocks) - 1) / 2)
        maze_width = int((len(blocks[0]) - 1) / 2)

        cells: list[list[Cell]] = []
        for cy in range(maze_height):
            cells.append([])
            for cx in range(maze_width):
                bx, by = cx * 2 + 1, cy * 2 + 1
                block = blocks[by][bx]
                cell: Cell = Cell(block.state.value, cx, cy)
                cell.walls["N"] = False if blocks[by - 1][bx].state == BlockState.EMPTY else True
                cell.walls["S"] = False if blocks[by + 1][bx].state == BlockState.EMPTY else True
                cell.walls["W"] = False if blocks[by][bx - 1].state == BlockState.EMPTY else True
                cell.walls["E"] = False if blocks[by][bx + 1].state == BlockState.EMPTY else True
                cells[cy].append(cell)
        return cells

    def handle_error(self, e: SizeException | AlgorithmException | SolvingException | ArgumentsException | MazeValidationException) -> None:
        CTkMessagebox(icon="warning", title=e.name, message=e.args[0])
