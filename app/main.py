from CTkMessagebox import CTkMessagebox
from customtkinter import *
from customtkinter import CTkFrame
from .maze import Maze, Cell, SizeException, AlgorithmException, SolvingException, ArgumentsException, \
    MazeValidationException
from .maze_builder import MazeBuilderWindow
from tkinter import Event
from .common import constants, Block, BlockState
import pickle

SETTINGS_FRAME_PADY: int = 5
SETTINGS_FRAME_PADX: int = 10
START_BUTTON_PADY: int = 5
START_BUTTON_PADX: int = 10
SETTING_TITLE_PADY: int = 0
SETTING_TITLE_PADX: int = 10

MODE_RADIO_PADY: int = 5
MODE_RADIO_PADX: int = 00
SIZE_PADY: int = 00
SIZE_PADX: int = 00
LINK_FILE_PADY: int = 0
LINK_FILE_PADX: int = 00
MAZE_BUILDER_PADY: int = 5
MAZE_BUILDER_PADX: int = 00

ABOUT_PADY: int = 30
ABOUT_PADX: int = 10


class MazeFrame(CTkFrame):
    master: CTk | CTkFrame
    widget_width: int = 0
    widget_height: int = 0
    lowest_size: int = 0
    canvas: CTkCanvas | None = None
    block_path: list[Block] = []
    start_block: Block | None = None
    exit_block: Block | None = None
    maze: Maze | None = None
    maze_width: int
    maze_height: int
    block_width: int
    block_height: int
    canvas_blocks: list[list[Block]] = []

    def __init__(self, master: CTk | CTkFrame):
        super().__init__(master)
        self.master: CTk = master

    def clear_data(self) -> None:
        self.block_path.clear()
        self.start_block = None
        self.exit_block = None

    def update_widget_size(self) -> None:
        self.master.update()
        self.update()
        self.widget_width = self.winfo_width()
        self.widget_height = self.winfo_height() - self.master.upper_panel.winfo_height()
        self.lowest_size = self.widget_width if self.widget_width < self.widget_height else self.widget_height

    def init_canvas(self) -> None:
        self.clear_data()
        self.update_widget_size()
        self.maze_width = self.maze.num_cols * 2 + 1
        self.maze_height = self.maze.num_rows * 2 + 1
        self.block_width = int(self.lowest_size / self.maze_width)
        self.block_height = int(self.lowest_size / self.maze_height)
        canvas_width = self.block_width * self.maze_width
        canvas_height = self.block_height * self.maze_height
        self.canvas = CTkCanvas(self, width=canvas_width, height=canvas_height)
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

    def reset_canvas_blocks(self) -> None:
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
                        self.canvas.itemconfig(self.canvas_blocks[y - 1][x].rectangle, fill=constants["EMPTY_COLOR"])
                    if not self.maze.grid[celly][cellx].walls["S"]:
                        self.canvas_blocks[y + 1][x].state = BlockState.EMPTY
                        self.canvas.itemconfig(self.canvas_blocks[y + 1][x].rectangle, fill=constants["EMPTY_COLOR"])
                    if not self.maze.grid[celly][cellx].walls["W"]:
                        self.canvas_blocks[y][x - 1].state = BlockState.EMPTY
                        self.canvas.itemconfig(self.canvas_blocks[y][x - 1].rectangle, fill=constants["EMPTY_COLOR"])
                    if not self.maze.grid[celly][cellx].walls["E"]:
                        self.canvas_blocks[y][x + 1].state = BlockState.EMPTY
                        self.canvas.itemconfig(self.canvas_blocks[y][x + 1].rectangle, fill=constants["EMPTY_COLOR"])

        self.canvas_blocks[self.maze.start_cell.y * 2 + 1][self.maze.start_cell.x * 2 + 1].state = BlockState.START
        self.canvas.itemconfig(self.start_block.rectangle, fill=constants["START_COLOR"])
        self.canvas_blocks[self.maze.exit_cell.y * 2 + 1][self.maze.exit_cell.x * 2 + 1].state = BlockState.EXIT
        self.canvas.itemconfig(self.exit_block.rectangle, fill=constants["EXIT_COLOR"])

    def draw_canvas(self) -> None:
        for y in range(0, self.maze_height):
            for x in range(0, self.maze_width):
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

                x1: int = x * self.block_width
                y1: int = y * self.block_height
                x2: int = (x + 1) * self.block_width
                y2: int = (y + 1) * self.block_height

                # radius: int = 2
                # points = [x1 + radius, y1,
                #           x1 + radius, y1,
                #           x2 - radius, y1,
                #           x2 - radius, y1,
                #           x2, y1,
                #           x2, y1 + radius,
                #           x2, y1 + radius,
                #           x2, y2 - radius,
                #           x2, y2 - radius,
                #           x2, y2,
                #           x2 - radius, y2,
                #           x2 - radius, y2,
                #           x1 + radius, y2,
                #           x1 + radius, y2,
                #           x1, y2,
                #           x1, y2 - radius,
                #           x1, y2 - radius,
                #           x1, y1 + radius,
                #           x1, y1 + radius,
                #           x1, y1]
                # self.canvas_blocks[y][x].rectangle = self.canvas.create_polygon(*points, **kwargs, smooth=True)

                points = [x1, y1, x2, y2]
                self.canvas_blocks[y][x].rectangle = self.canvas.create_rectangle(*points, **kwargs)

    def draw_path(self) -> None:
        self.block_path = []
        self.reset_canvas_blocks()
        path = self.maze.path

        prev_block = self.start_block

        for cc in path:
            block = self.canvas_blocks[cc.y * 2 + 1][cc.x * 2 + 1]
            block.state = BlockState.PATH
            self.canvas.itemconfig(block.rectangle, fill=constants["PATH_COLOR"])

            block2 = self.canvas_blocks[block.y + int((prev_block.y - block.y) / 2)][
                block.x + int((prev_block.x - block.x) / 2)]
            block2.state = BlockState.PATH
            self.canvas.itemconfig(block2.rectangle, fill=constants["PATH_COLOR"])

            self.block_path.append(block2)
            self.block_path.append(block)

            prev_block = block

        block2 = self.canvas_blocks[self.exit_block.y + int((prev_block.y - self.exit_block.y) / 2)][
            self.exit_block.x + int((prev_block.x - self.exit_block.x) / 2)]
        block2.state = BlockState.PATH
        self.canvas.itemconfig(block2.rectangle, fill=constants["PATH_COLOR"])
        self.block_path.append(block2)

    def is_straight_to(self, block1: Block, block2: Block) -> bool:
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

    def left_click_event(self, event: Event) -> None:
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

            is_block_next_to_exit: bool = True

            diff_x = abs(block_x - self.exit_block.x)
            diff_y = abs(block_y - self.exit_block.y)

            if diff_x + diff_y >= 2 or diff_x + diff_y == 0:
                is_block_next_to_exit = False
            if is_block_next_to_exit:
                CTkMessagebox(icon="check", title="Победа", message="Вы успешно прошли лабиринт!")

    def right_click_event(self, event: Event) -> None:
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
            rest_block_path = self.block_path[index + 1:]
            self.block_path = self.block_path[:index + 1]
            for block in rest_block_path:
                block.state = BlockState.EMPTY
                self.canvas.itemconfig(block.rectangle, fill=constants["EMPTY_COLOR"])


class App(CTk):
    maze_frame: MazeFrame
    upper_panel: CTkFrame
    return_button: CTkButton
    filepath: str = ""
    custom_grid: list[list[Cell]] | None = None
    controls_menu: CTkFrame
    mode_custom: BooleanVar
    size_text: CTkLabel
    size_str: StringVar
    size_entry: CTkEntry
    link_file_button: CTkButton
    info_label: CTkLabel
    maze_builder_button: CTkButton
    start_button: CTkButton
    game_menu: CTkFrame
    maze_builder: MazeBuilderWindow

    def __init__(self):
        super().__init__()

        self.title("Maze")
        self.resizable(False, False)
        self.geometry("1125x800")
        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=1, uniform="group1")
        self.grid_columnconfigure(2, weight=1, uniform="group1")

        self.grid_columnconfigure(0, weight=1, uniform="group4")
        self.grid_columnconfigure(1, weight=1, uniform="group4")
        self.grid_columnconfigure(2, weight=1, uniform="group4")

        self.init_upper_panel()
        self.init_controls_menu()
        self.maze_frame = MazeFrame(self)
        self.maze_frame.grid(column=1, row=1, columnspan=2, rowspan=2, sticky="news")

    def init_upper_panel(self) -> None:
        self.upper_panel = CTkFrame(self)
        self.upper_panel.grid(column=0, row=0, columnspan=3, sticky="new")

        self.upper_panel.grid_columnconfigure((0, 1, 2), weight=1)
        self.upper_panel.grid_rowconfigure(0, weight=1)

        self.return_button = CTkButton(self.upper_panel, text="Закончить и выйти", command=self.go_back)
        self.return_button_hide()
        title_label = CTkLabel(self.upper_panel, text="Лабиринт")
        title_label.grid(row=0, column=1, sticky="n")
        exit_button = CTkButton(self.upper_panel, text="Выйти из игры", command=sys.exit)
        exit_button.grid(row=0, column=2, sticky="ne")

    def return_button_show(self) -> None:
        self.return_button.grid(row=0, column=0, sticky="nw")

    def return_button_hide(self) -> None:
        self.return_button.grid_forget()

    def go_back(self) -> None:
        self.return_button_hide()
        self.maze_frame.canvas.place_forget()
        self.game_menu.grid_forget()
        self.controls_menu.grid(column=0, row=1, sticky="news")

    def init_controls_menu(self) -> None:
        self.custom_grid: list[list[Cell]] | None = None
        self.controls_menu = CTkFrame(self)
        self.controls_menu.grid(column=0, row=1, sticky="news")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=8)
        self.grid_rowconfigure(2, weight=1)

        settings_label = CTkLabel(self.controls_menu, text="Настройки")
        settings_label.grid(row=0, column=0, sticky=N + W)
        settings_label.grid_configure(pady=SETTING_TITLE_PADY, padx=SETTING_TITLE_PADX)

        settings_frame = CTkFrame(self.controls_menu)
        settings_frame.grid(row=1, column=0, sticky=W + E + N + S)
        settings_frame.grid_configure(pady=SETTINGS_FRAME_PADY, padx=SETTINGS_FRAME_PADX)

        self.mode_custom = BooleanVar()
        self.mode_custom.set(False)
        mode_radio_random = CTkRadioButton(settings_frame, text="Случайный", variable=self.mode_custom,
                                           value=False, command=self.random_click)
        mode_radio_random.grid(row=0, column=0)
        mode_radio_custom = CTkRadioButton(settings_frame, text="Свой", variable=self.mode_custom, value=True,
                                           command=self.custom_click)
        mode_radio_custom.grid(row=0, column=1)
        mode_radio_random.grid_configure(pady=MODE_RADIO_PADY, padx=MODE_RADIO_PADX)
        mode_radio_custom.grid_configure(pady=MODE_RADIO_PADY, padx=MODE_RADIO_PADX)

        self.size_text = CTkLabel(settings_frame, text="Размер")
        self.size_str = StringVar()
        self.size_str.set("")
        self.size_entry = CTkEntry(settings_frame, textvariable=self.size_str)
        self.size_entry.configure(validate='all', validatecommand=(self.register(self.size_validate), '%P'))

        self.link_file_button = CTkButton(settings_frame, text="Прикрепить файл", command=self.open_file)
        self.info_label = CTkLabel(settings_frame, text="")
        self.maze_builder_button = CTkButton(settings_frame, text="Построитель лабиринтов",
                                             command=self.launch_maze_builder)
        self.random_click()

        self.start_button = CTkButton(self.controls_menu, text="Начать игру", command=self.start_game)
        self.start_button.grid(row=2, column=0, sticky=W + E + N + S)
        self.start_button.grid_configure(pady=START_BUTTON_PADY, padx=START_BUTTON_PADX)

        about_all_frame = CTkFrame(self)
        about_all_frame.grid(row=2, column=0, sticky=W+N+E+S)

        about_frame = CTkFrame(about_all_frame)
        about_frame.grid(row=0, column=0, sticky=W+E+S)
        about_frame.grid_configure(pady=ABOUT_PADY, padx=ABOUT_PADX)

        about_label = CTkLabel(about_frame, text="О программе")
        about_label.grid(row=0, column=0, columnspan=2, sticky=W)
        about_label.grid_configure(pady=5, padx=5)

        about_program_button = CTkButton(about_frame, text="Справка", command=self.open_about_program)
        about_program_button.grid(row=1, column=0, sticky=W)
        about_program_button.grid_configure(pady=LINK_FILE_PADY, padx=LINK_FILE_PADX)
        about_dev_button = CTkButton(about_frame, text="О разработчике", command=self.open_about_dev)
        about_dev_button.grid(row=1, column=1, sticky=E)
        about_dev_button.grid_configure(pady=5, padx=5)

    def open_about_program(self) -> None:
        CTkMessagebox(title="Справка", width=800,
                      message="Данная программа позволяет Вам создавать и проходить лабиринты.\nЧтобы создать "
                              "случайный лабиринт выберите \"Случайный\" тип, задайте размер и нажмите \"Начать "
                              "игру\".\nЧтобы создать свой лабиринт выберите \"Свой\", экспортируйте свой лабиринт в "
                              "\"Построителе лабиринтов\" и прикрепите файл используя \"Прикрепить файл\".")

    def open_about_dev(self) -> None:
        CTkMessagebox(title="О разработчике", width=800,
                      message="Разработчик: Иван Лифанов.\nИсходный код: github.com/bmg-c/labyrinthGame")

    def launch_maze_builder(self) -> None:
        self.maze_builder = MazeBuilderWindow(self)
        self.maze_builder.update_widget_size()

    def size_validate(self, value: str) -> bool:
        size_str: str = value
        if size_str == "":
            return True
        if not size_str.isnumeric():
            return False
        return True

    def open_file(self) -> None:
        filepath = filedialog.askopenfile()
        filepath = filepath.name
        filehandler = open(filepath, 'rb')
        try:
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

        self.custom_grid = cells
        self.info_label.configure(text="Прикреплено!")

    def random_click(self) -> None:
        self.size_text.grid(row=1, column=0)
        self.size_entry.grid(row=1, column=1)
        self.size_text.grid_configure(pady=SIZE_PADY, padx=SIZE_PADX)
        self.size_entry.grid_configure(pady=SIZE_PADY, padx=SIZE_PADX)
        self.link_file_button.grid_forget()
        self.info_label.grid_forget()
        self.size_entry.configure(state=NORMAL)
        self.maze_builder_button.grid_forget()

    def custom_click(self) -> None:
        self.size_text.grid_forget()
        self.size_entry.grid_forget()
        self.link_file_button.grid(row=2, column=0)
        self.link_file_button.grid_configure(pady=LINK_FILE_PADY, padx=LINK_FILE_PADX)
        self.info_label.grid(row=2, column=1)
        self.info_label.grid_configure(pady=LINK_FILE_PADY, padx=LINK_FILE_PADX)
        self.size_entry.configure(state=DISABLED)
        self.maze_builder_button.grid(row=3, column=0, columnspan=2, sticky="nswe")
        self.maze_builder_button.grid_configure(pady=MAZE_BUILDER_PADY, padx=MAZE_BUILDER_PADX)

    def start_game(self) -> None:
        if self.mode_custom.get() and self.custom_grid is not None:
            try:
                self.maze_frame.maze = Maze(custom_grid=self.custom_grid)
            except Exception as e:
                self.handle_error(e)
                return
        elif self.mode_custom.get() and self.custom_grid is None:
            CTkMessagebox(icon="info", title="Прикрепление лабиринта",
                          message="Вам необходимо прикрепить файл с лабиринтом. Его можно создать используя "
                                  "\"Построитель лабирнитов\"")
            return
        elif self.size_str.get() == "":
            CTkMessagebox(icon="info", title="Введите размер",
                          message="Для генерации лабиринта Вы должны вписать нужный размер")
            return
        else:
            try:
                size: int = int(self.size_str.get())
                self.maze_frame.maze = Maze(num_rows=size, num_cols=size)
            except Exception as e:
                self.handle_error(e)
                return

        self.maze_frame.init_canvas()
        self.maze_frame.draw_canvas()

        self.return_button_show()
        self.controls_menu.grid_forget()
        self.init_game_menu()

    def init_game_menu(self) -> None:
        self.game_menu = CTkFrame(self)
        self.game_menu.grid(row=1, column=0, sticky="nswe")
        game_menu_title_label = CTkLabel(self.game_menu, text="Меню игры")
        game_menu_title_label.grid(row=0, column=1, sticky="sw")
        help_button = CTkButton(self.game_menu, text="Помощь по игре", command=self.help_popup)
        help_button.grid(row=1, column=1, sticky="nwe")
        game_rules_label = CTkLabel(self.game_menu,
                                    text="Правила игры:\nЛКМ - рисование пути\nПКМ - стирание пути")
        game_rules_label.grid(row=2, column=1, sticky="nswe")
        give_up_button = CTkButton(self.game_menu, text="Сдаться", command=self.give_up)
        give_up_button.grid(row=3, column=1, sticky="swe")

    def give_up(self) -> None:
        self.maze_frame.draw_path()
        CTkMessagebox(icon="info", title="Вы сдались", message="Теперь на экране покажется верный путь")

    def help_popup(self) -> None:
        CTkMessagebox(icon="info", title="Помощь по игре",
                      message="В этой игре Вам необходимо пройти лабиринт, рисуя путь от начальной синей клетки до "
                              "конечной используя левую кнопку мыши для рисования пути и правой кнопки мыши для "
                              "стирания пути.")

    def handle_error(self,
                     e: SizeException | AlgorithmException | SolvingException | ArgumentsException | MazeValidationException) -> None:
        CTkMessagebox(icon="warning", title=e.name, message=e.args[0])
