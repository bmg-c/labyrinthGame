from CTkMessagebox import CTkMessagebox
from customtkinter import *
from customtkinter import CTkFrame
from maze import Maze, Cell
from maze_builder import MazeBuilderWindow
from tkinter import Event
from enum import Enum
from common import constants, Block, BlockState
import pickle


def cell_next_to(x0, y0, x1, y1):
    diff_x = abs(x0 - x1)
    diff_y = abs(y0 - y1)

    if diff_x + diff_y >= 2 or diff_x + diff_y == 0:
        return False
    return True


class MazeFrame(CTkFrame):
    def __init__(self, master: CTk | CTkFrame):
        super().__init__(master)
        self.master: CTk = master
        self.widget_width = 0
        self.widget_height = 0
        self.lowest_size = 0
        self.canvas = None
        self.block_path = []
        self.start_block = None
        self.exit_block = None

        self.maze: Maze | None = None

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
        self.canvas.bind("<B1-Motion>", self.left_click_event)
        self.canvas.bind("<Button-1>", self.left_click_event)
        self.canvas.bind("<B3-Motion>", self.right_click_event)
        self.canvas.bind("<Button-3>", self.right_click_event)

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
        self.start_block = self.canvas_blocks[self.maze.start_cell.y * 2 + 1][self.maze.start_cell.x * 2 + 1]
        self.canvas_blocks[self.maze.exit_cell.y * 2 + 1][self.maze.exit_cell.x * 2 + 1].state = BlockState.EXIT
        self.exit_block = self.canvas_blocks[self.maze.exit_cell.y * 2 + 1][self.maze.exit_cell.x * 2 + 1]

    def reset_canvas_blocks(self):
        self.block_path = []
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                self.canvas_blocks[y][x].state = BlockState.WALL
                self.canvas.itemconfig(self.canvas_blocks[y][x].rectangle, fill=constants["WALL_COLOR"])

        for y in range(len(self.canvas_blocks)):
            for x in range(len(self.canvas_blocks[0])):
                if x % 2 == 1 and y % 2 == 1:
                    self.canvas_blocks[y][x].state = BlockState.EMPTY
                    self.canvas.itemconfig(self.canvas_blocks[y][x].rectangle, fill=constants["EMPTY_COLOR"])
                    cellx, celly = int((x - 1) / 2), int((y - 1) / 2)  # 0,0-1,1  0,1-1,3  0,2-1,5
                    if not self.maze.grid[celly][cellx].walls["N"]:
                        self.canvas_blocks[y - 1][x].state = BlockState.EMPTY
                        self.canvas.itemconfig(self.canvas_blocks[y-1][x].rectangle, fill=constants["EMPTY_COLOR"])
                    if not self.maze.grid[celly][cellx].walls["S"]:
                        self.canvas_blocks[y + 1][x].state = BlockState.EMPTY
                        self.canvas.itemconfig(self.canvas_blocks[y+1][x].rectangle, fill=constants["EMPTY_COLOR"])
                    if not self.maze.grid[celly][cellx].walls["W"]:
                        self.canvas_blocks[y][x - 1].state = BlockState.EMPTY
                        self.canvas.itemconfig(self.canvas_blocks[y][x-1].rectangle, fill=constants["EMPTY_COLOR"])
                    if not self.maze.grid[celly][cellx].walls["E"]:
                        self.canvas_blocks[y][x + 1].state = BlockState.EMPTY
                        self.canvas.itemconfig(self.canvas_blocks[y][x+1].rectangle, fill=constants["EMPTY_COLOR"])

        self.canvas_blocks[self.maze.start_cell.y * 2 + 1][self.maze.start_cell.x * 2 + 1].state = BlockState.START
        self.canvas.itemconfig(self.start_block.rectangle, fill=constants["START_COLOR"])
        self.canvas_blocks[self.maze.exit_cell.y * 2 + 1][self.maze.exit_cell.x * 2 + 1].state = BlockState.EXIT
        self.canvas.itemconfig(self.exit_block.rectangle, fill=constants["EXIT_COLOR"])

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

    def draw_path(self):
        self.block_path = []
        self.reset_canvas_blocks()
        path = self.maze.path

        prev_block = self.start_block

        for cc in path:
            block = self.canvas_blocks[cc.y * 2 + 1][cc.x * 2 + 1]
            block.state = BlockState.PATH
            self.canvas.itemconfig(block.rectangle, fill=constants["PATH_COLOR"])

            block2 = self.canvas_blocks[block.y + int((prev_block.y - block.y) / 2)][block.x + int((prev_block.x - block.x) / 2)]
            block2.state = BlockState.PATH
            self.canvas.itemconfig(block2.rectangle, fill=constants["PATH_COLOR"])

            self.block_path.append(block2)
            self.block_path.append(block)

            prev_block = block

        block2 = self.canvas_blocks[self.exit_block.y + int((prev_block.y - self.exit_block.y) / 2)][self.exit_block.x + int((prev_block.x - self.exit_block.x) / 2)]
        block2.state = BlockState.PATH
        self.canvas.itemconfig(block2.rectangle, fill=constants["PATH_COLOR"])
        self.block_path.append(block2)

    def is_straight_to(self, block1, block2) -> bool:
        # return True
        if block1.x == block2.x:
            x = block1.x
            diff = 1
            y = block1.y + 1
            if block1.y > block2.y:
                diff = -1
                y = block1.y - 1

            while y != block2.y:
                if self.canvas_blocks[y][x].state != BlockState.EMPTY:
                    return False
                y += diff
        elif block1.y == block2.y:
            y = block1.y
            diff = 1
            x = block1.x + 1
            if block1.x > block2.x:
                diff = -1
                x = block1.x - 1

            while x != block2.x:
                if self.canvas_blocks[y][x].state != BlockState.EMPTY:
                    return False
                x += diff
        else:
            return False
        return True

    def left_click_event(self, event: Event):
        if self.canvas is None:
            return
        block_x = int(event.x / self.block_width)
        block_y = int(event.y / self.block_height)
        clicked_block = self.canvas_blocks[block_y][block_x]

        if clicked_block.state == BlockState.EMPTY:
            if len(self.block_path) == 0:
                last_block = self.start_block
            else:
                last_block = self.block_path[-1]

            if not self.is_straight_to(last_block, clicked_block):
                return
            print(clicked_block)

            if last_block.x == clicked_block.x:
                x = last_block.x
                diff = 1
                y = last_block.y + 1
                if last_block.y > clicked_block.y:
                    diff = -1
                    y = last_block.y - 1

                while y != clicked_block.y:
                    block = self.canvas_blocks[y][x]
                    self.block_path.append(block)
                    block.state = BlockState.PATH
                    self.canvas.itemconfig(block.rectangle, fill=constants["PATH_COLOR"])
                    y += diff
                self.block_path.append(clicked_block)
                clicked_block.state = BlockState.PATH
                self.canvas.itemconfig(clicked_block.rectangle, fill=constants["PATH_COLOR"])
            elif last_block.y == clicked_block.y:
                y = last_block.y
                diff = 1
                x = last_block.x + 1
                if last_block.x > clicked_block.x:
                    diff = -1
                    x = last_block.x - 1

                while x != clicked_block.x:
                    block = self.canvas_blocks[y][x]
                    self.block_path.append(block)
                    block.state = BlockState.PATH
                    self.canvas.itemconfig(block.rectangle, fill=constants["PATH_COLOR"])
                    x += diff
                self.block_path.append(clicked_block)
                clicked_block.state = BlockState.PATH
                self.canvas.itemconfig(clicked_block.rectangle, fill=constants["PATH_COLOR"])
            else:
                print("Return")
                return

            if cell_next_to(block_x, block_y, self.exit_block.x, self.exit_block.y):
                print("End!!!")

            # if not cell_next_to(block_x, block_y, last_block.x, last_block.y):
            #     return
            #
            # if cell_next_to(block_x, block_y, self.exit_block.x, self.exit_block.y):
            #     print("End!!!")
            #
            # self.block_path.append(clicked_block)
            # clicked_block.state = BlockState.PATH
            # self.canvas.itemconfig(clicked_block.rectangle, fill=constants["PATH_COLOR"])

    def right_click_motion_event(self, event: Event):
        if self.canvas is None:
            return
        block_x = int(event.x / self.block_width)
        block_y = int(event.y / self.block_height)
        clicked_block = self.canvas_blocks[block_y][block_x]

        if clicked_block.state == BlockState.PATH:
            if len(self.block_path) == 0:
                return
            else:
                last_block = self.block_path[-1]

            if clicked_block is not last_block:
                return

            self.block_path.pop()
            clicked_block.state = BlockState.EMPTY
            self.canvas.itemconfig(clicked_block.rectangle, fill=constants["EMPTY_COLOR"])

    def right_click_event(self, event: Event):
        if self.canvas is None:
            return
        block_x = int(event.x / self.block_width)
        block_y = int(event.y / self.block_height)
        clicked_block = self.canvas_blocks[block_y][block_x]

        if clicked_block.state == BlockState.PATH:
            if len(self.block_path) == 0:
                return
            if clicked_block is self.block_path[-1]:
                clicked_block.state = BlockState.EMPTY
                self.canvas.itemconfig(clicked_block.rectangle, fill=constants["EMPTY_COLOR"])
                self.block_path.pop()
                return


            index = self.block_path.index(clicked_block)
            rest_block_path = self.block_path[index+1:]
            self.block_path = self.block_path[:index+1]
            for block in rest_block_path:
                block.state = BlockState.EMPTY
                self.canvas.itemconfig(block.rectangle, fill=constants["EMPTY_COLOR"])


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

    def init_upper_panel(self):
        self.upper_panel = CTkFrame(self)

        self.upper_panel.grid_columnconfigure((0, 1, 2), weight=1)
        self.upper_panel.grid_rowconfigure(0, weight=1)

        self.return_button = CTkButton(self.upper_panel, text="Закончить и выйти", command=self.go_back)
        self.return_button_hide()
        self.title_label = CTkLabel(self.upper_panel, text="Лабиринт")
        self.title_label.grid(row=0, column=1, sticky="n")
        self.exit_button = CTkButton(self.upper_panel, text="Выйти из игры", command=self.destroy)
        self.exit_button.grid(row=0, column=2, sticky="ne")

    def return_button_show(self) -> None:
        self.return_button.grid(row=0, column=0, sticky="nw")

    def return_button_hide(self) -> None:
        self.return_button.grid_forget()

    def go_back(self) -> None:
        self.return_button_hide()
        self.maze_frame.canvas.place_forget()
        self.game_menu.grid_forget()
        self.controls_menu.grid(column=0, row=1, sticky="news")

    def init_controls_menu(self):
        self.filepath = ""
        self.custom_grid: list[list[Cell]] | None = None
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

        self.link_file_button = CTkButton(self.settings_frame, text="Прикрепить файл", command=self.open_file)
        self.info_label= CTkLabel(self.settings_frame, text="")
        self.maze_builder_button = CTkButton(self.settings_frame, text="Построитель лабиринтов", command=self.launch_maze_builder)
        self.random_click()

        self.start_button = CTkButton(self.controls_menu, text="Начать игру", command=self.start_game)
        self.start_button.grid(row=2, column=0, sticky=W+E+N+S)

    def launch_maze_builder(self):
        self.maze_builder = MazeBuilderWindow(self)
        self.maze_builder.update_widget_size()

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
        filepath = filepath.name
        filehandler = open(filepath, 'rb')
        try:
            cells: list[list[Cell]] = pickle.load(filehandler)
        except:
            CTkMessagebox(icon="warning", title="Ошибка валидации", message="Произошла ошибка валидации")
            return

        num_rows = len(cells)
        if num_rows <= 2:
            CTkMessagebox(icon="warning", title="Ошибка валидации", message="Произошла ошибка валидации")
            return
        num_cols = len(cells[0])
        if num_cols <= 2:
            CTkMessagebox(icon="warning", title="Ошибка валидации", message="Произошла ошибка валидации")
            return
        if num_rows != num_cols:
            CTkMessagebox(icon="warning", title="Ошибка валидации", message="Произошла ошибка валидации")
            return

        self.custom_grid = cells
        self.info_label.configure(text="Прикреплено!")

    def random_click(self):
        self.link_file_button.grid_forget()
        self.info_label.grid_forget()
        self.size_entry.configure(state=NORMAL)
        self.maze_builder_button.grid_forget()

    def custom_click(self):
        self.link_file_button.grid(row=3, column=0)
        self.info_label.grid(row=3, column=1)
        self.size_entry.configure(state=DISABLED)
        self.maze_builder_button.grid(row=4, column=0, columnspan=2, sticky="nswe")

    def start_game(self):
        if self.mode_custom.get() and self.custom_grid is not None:
            self.maze_frame.maze = Maze(custom_grid=self.custom_grid)
        elif self.mode_custom.get() and self.custom_grid is None:
            CTkMessagebox(icon="warning", title="Ошибка валидации", message="Произошла ошибка валидации")
            return
        elif self.size_str.get() == "":
            CTkMessagebox(icon="warning", title="Ошибка валидации", message="Произошла ошибка валидации")
            return
        else:
            size: int = int(self.size_str.get())
            self.maze_frame.maze = Maze(num_rows=size, num_cols=size)

        self.maze_frame.init_canvas()
        self.maze_frame.draw_canvas()

        self.return_button_show()
        self.controls_menu.grid_forget()
        self.init_game_menu()

    def init_game_menu(self):
        self.game_menu = CTkFrame(self)
        self.game_menu.grid(row=1, column=0, sticky="nswe")
        self.game_menu_title_label = CTkLabel(self.game_menu, text="Меню игры")
        self.game_menu_title_label.grid(row=0, column=1, sticky="sw")
        self.help_button = CTkButton(self.game_menu, text="Помощь по игре", command=self.help_popup)
        self.help_button.grid(row=1, column=1, sticky="nwe")
        self.game_rules_label = CTkLabel(self.game_menu, text="Правила игры:\nЛКМ - рисование пути\nПКМ - стирание пути")
        self.game_rules_label.grid(row=2, column=1, sticky="nswe")
        self.give_up_button = CTkButton(self.game_menu, text="Сдаться", command=self.give_up)
        self.give_up_button.grid(row=3, column=1, sticky="swe")

    def give_up(self):
        self.maze_frame.draw_path()

    def help_popup(self):
        CTkMessagebox(icon="info", title="Ошибка валидации", message="Произошла ошибка валидации")

app = App()
app.mainloop()
