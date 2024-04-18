from customtkinter import *
from customtkinter import CTkFrame
from maze import Maze
from tkinter import Event
from enum import Enum


constants = {
    "START_COLOR": "blue",
    "EXIT_COLOR": "blue",
    "WALL_COLOR": "black",
    "PATH_COLOR": "green",
    "EMPTY_COLOR": "#ddd",
}


class BlockState(Enum):
    WALL = 0
    EMPTY = 1
    PATH = 2
    START = 3
    EXIT = 4


class Block:
    def __init__(self, x, y, state: BlockState):
        self.x = x
        self.y = y
        self.state = state
        self.rectangle = None


def cell_next_to(x0, y0, x1, y1):
    diff_x = abs(x0 - x1)
    diff_y = abs(y0 - y1)

    if diff_x + diff_y >= 2 or diff_x + diff_y == 0:
        return False
    return True


class MazeFrame(CTkFrame):
    def __init__(self, master):
        # super().__init__(master, width=700, height=700)
        super().__init__(master)
        self.master = master
        self.widget_width = 0
        self.widget_height = 0
        self.lowest_size = 0
        self.canvas = None
        self.block_path = []
        self.path = []

        self.maze = Maze(30, 30)

        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        self.update_widget_size()
        # self.canvas.pack(anchor="center")
        # self.canvas.pack(expand=YES, fill=BOTH, anchor="center")

    def update_widget_size(self):
        self.master.update()
        self.update()
        self.widget_width = self.winfo_width()
        self.widget_height = self.winfo_height()
        self.lowest_size = self.widget_width if self.widget_width < self.widget_height else self.widget_height

    def init_canvas(self):
        self.update_widget_size()
        print(f"{self.widget_width}x{self.widget_height}")
        self.maze_width = self.maze.num_cols * 2 + 1
        self.maze_height = self.maze.num_rows * 2 + 1
        self.block_width = int(self.lowest_size / self.maze_width)
        self.block_height = int(self.lowest_size / self.maze_height)
        self.canvas_width = self.block_width * self.maze_width
        self.canvas_height = self.block_height * self.maze_height
        print(f"{self.canvas_width}x{self.canvas_height}")
        self.canvas = CTkCanvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.canvas.bind("<B1-Motion>", self.left_click_motion_event)
        self.canvas.bind("<B3-Motion>", self.right_click_motion_event)

        self.canvas_blocks: list[list[Block]] = []
        for y in range(self.maze_height):
            self.canvas_blocks.append([])
            for x in range(self.maze_width):
                self.canvas_blocks[y].append(Block(x, y, BlockState.WALL))


        for y in range(len(self.canvas_blocks)):
            for x in range(len(self.canvas_blocks[0])):
                if x % 2 == 1 and y % 2 == 1:
                    self.canvas_blocks[y][x].state = BlockState.EMPTY
                    cellx, celly = int((x - 1) / 2), int((y - 1) / 2)  # 0,0-1,1  0,1-1,3  0,2-1,5
                    if not self.maze.grid[celly][cellx].walls["N"]:
                        self.canvas_blocks[y - 1][x].state = BlockState.EMPTY
                    if not self.maze.grid[celly][cellx].walls["S"]:
                        self.canvas_blocks[y + 1][x].state = BlockState.EMPTY
                    if not self.maze.grid[celly][cellx].walls["W"]:
                        self.canvas_blocks[y][x - 1].state = BlockState.EMPTY
                    if not self.maze.grid[celly][cellx].walls["E"]:
                        self.canvas_blocks[y][x + 1].state = BlockState.EMPTY

        self.canvas_blocks[self.maze.start_cell.y * 2 + 1][self.maze.start_cell.x * 2 + 1].state = BlockState.START
        self.canvas_blocks[self.maze.exit_cell.y * 2 + 1][self.maze.exit_cell.x * 2 + 1].state = BlockState.EXIT

    def draw_canvas(self):
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

    def left_click_motion_event(self, event: Event):
        if self.canvas is None:
            return
        block_x = int(event.x / self.block_width)
        block_y = int(event.y / self.block_height)
        print(f"({block_x}, {block_y})")

        state = self.canvas_blocks[block_y][block_x].state
        if state == BlockState.EMPTY:
            # if len(self.block_path) == 0 and not cell_next_to(block_x, block_y, self.maze.start_cell.x, self.maze.start_cell.y):
            #     return
            # last_block = self.block_path[len(self.block_path) - 1]
            # elif cell_next_to(block_x, block_y, last_block.x, last_block.y
            self.canvas_blocks[block_y][block_x].state = BlockState.PATH
            self.canvas.itemconfig(self.canvas_blocks[block_y][block_x].rectangle, fill=constants["PATH_COLOR"])



            return

    def right_click_motion_event(self, event: Event):
        if self.canvas is None:
            return
        block_x = int(event.x / self.block_width)
        block_y = int(event.y / self.block_height)
        print(f"({block_x}, {block_y})")

        state = self.canvas_blocks[block_y][block_x].state
        if state == BlockState.PATH:
            self.canvas_blocks[block_y][block_x].state = BlockState.EMPTY
            self.canvas.itemconfig(self.canvas_blocks[block_y][block_x].rectangle, fill=constants["EMPTY_COLOR"])

            return


class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("Maze")
        self.resizable(False, False)
        self.geometry("1125x800")
        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=1, uniform="group1")
        self.grid_columnconfigure(2, weight=1, uniform="group1")

        self.init_upper_panel()
        self.upper_panel.grid(column=0, row=0, columnspan=3, sticky="new")

        self.init_controls_menu()
        self.controls_menu.grid(column=0, row=1, sticky="news")

        self.maze_frame = MazeFrame(self)
        self.maze_frame.grid(column=1, row=1, columnspan=2, sticky="news")
        self.maze_frame.init_canvas()
        self.maze_frame.draw_canvas()

        # self.maze_frame.update()
        # print(self.maze_frame.winfo_height())

    def init_upper_panel(self):
        self.upper_panel = CTkFrame(self)

        self.upper_panel.grid_columnconfigure((0, 1, 2), weight=1)
        self.upper_panel.grid_rowconfigure(0, weight=1)

        self.return_button = CTkButton(self.upper_panel, text="Вернуться")
        self.return_button_hide()
        self.title_label = CTkLabel(self.upper_panel, text="Лабиринт")
        self.title_label.grid(row=0, column=1, sticky="n")
        self.exit_button = CTkButton(self.upper_panel, text="Выйти из игры", command=self.destroy)
        self.exit_button.grid(row=0, column=2, sticky="ne")

    def return_button_show(self) -> None:
        self.return_button.grid(row=0, column=0, sticky="nw")

    def return_button_hide(self) -> None:
        self.return_button.grid_forget()

    def init_controls_menu(self):
        self.filepath = ""
        self.controls_menu = CTkFrame(self)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=8)
        self.grid_rowconfigure(2, weight=1)

        self.settings_label = CTkLabel(self.controls_menu, text="Настройки")
        self.settings_label.grid(row=0, column=0, sticky=N+W)

        self.settings_frame = CTkFrame(self.controls_menu)
        self.settings_frame.grid(row=1, column=0, sticky=W+E+N+S)

        self.mode_custom = BooleanVar()
        self.mode_custom.set(False)
        self.mode_radio_random = CTkRadioButton(self.settings_frame, text="Случайный", variable=self.mode_custom, value=False, command=self.random_click)
        self.mode_radio_random.grid(row=0, column=0)
        self.mode_radio_custom = CTkRadioButton(self.settings_frame, text="Свой", variable=self.mode_custom, value=True, command=self.custom_click)
        self.mode_radio_custom.grid(row=1, column=0)

        self.size_text = CTkLabel(self.settings_frame, text="Размер")
        self.size_text.grid(row=2, column=0)
        self.size_str = StringVar()
        self.size_str.set("")
        self.size_entry = CTkEntry(self.settings_frame, textvariable=self.size_str)
        self.size_entry.configure(validate='all', validatecommand=(self.register(self.size_validate), '%P', '%V'))
        self.size_entry.grid(row=2, column=1)

        self.generate_button = CTkButton(self.settings_frame, text="Сгенерировать", command=self.generate_labyrinth)
        self.link_file_button = CTkButton(self.settings_frame, text="Прикрепить файл", command=self.open_file)
        self.info_label = CTkLabel(self.settings_frame, text="")
        self.random_click()
        self.info_label.grid(row=3, column=1, sticky=W+N+S+N)

        self.start_button = CTkButton(self.controls_menu, text="Начать игру")
        self.start_button.grid(row=2, column=0, sticky=W+E+N+S)

    def generate_labyrinth(self):
        size_str = self.size_str.get()
        error = False
        msg = ""
        if size_str == "":
            error = True
            msg = "Введите размер лабиринта"
        elif int(size_str) > 20 or int(size_str) < 5:
            error = True
            msg = "Размер лабиринта должен быть не меньше 5 и не больше 20"
        if error:
            self.info_label.configure(text=msg)
            return

    def size_validate(self, value, state):
        print(state)
        size_str: str = value
        print(size_str)
        if size_str == "":
            return True
        if not size_str.isnumeric():
            return False
        return True

    def open_file(self):
        filepath = filedialog.askopenfile()
        self.filepath = filepath.name
        print(self.filepath)

    def random_click(self):
        self.link_file_button.grid_forget()
        self.generate_button.grid(row=3, column=0)
        self.size_entry.configure(state=NORMAL)

    def custom_click(self):
        self.generate_button.grid_forget()
        self.link_file_button.grid(row=3, column=0)
        self.size_entry.configure(state=DISABLED)


app = App()
app.mainloop()
