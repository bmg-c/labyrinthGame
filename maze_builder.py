from customtkinter import *
import pickle
from enum import Enum
from common import Block, BlockState
from maze import Cell, CellState, Maze
from tkinter import filedialog


def save_grid_to_file(grid: list[list[Cell]], filepath: str) -> None:
    filehandler = open(filepath, 'wb')
    pickle.dump(grid, filehandler, pickle.HIGHEST_PROTOCOL)


def read_grid_from_file(filepath: str) -> list[list[Cell]]:
    filehandler = open(filepath, 'rb')
    return pickle.load(filehandler)


def cell_next_to(x0, y0, x1, y1):
    diff_x = abs(x0 - x1)
    diff_y = abs(y0 - y1)

    if diff_x + diff_y >= 2 or diff_x + diff_y == 0:
        return False
    return True


class MazeBuilderWindow(CTkToplevel):
    def __init__(self, master: CTk):
        super().__init__(master)
        self.filepath: str = ""

        self.title("Maze Builder")
        self.geometry("750x800")
        self.columnconfigure(0, weight=1, uniform="group2")
        # self.rowconfigure((0, 1), uniform="group3")
        self.rowconfigure(2, weight=1, uniform="group3")
        self.resizable(False, False)

        self.init_upper_panel()
        self.upper_panel.grid(row=0, column=0, sticky="new")

        self.init_control_bar()
        self.control_bar.grid(row=1, column=0, sticky="new")

    def init_upper_panel(self):
        self.upper_panel = CTkFrame(self)

        self.upper_panel.grid_columnconfigure((0, 1), weight=1)
        self.upper_panel.grid_rowconfigure(0, weight=1)

        self.title_label = CTkLabel(self.upper_panel, text="Построитель лабиринтов")
        self.title_label.grid(row=0, column=0, sticky="n")
        self.exit_button = CTkButton(self.upper_panel, text="Закрыть", command=self.destroy)
        self.exit_button.grid(row=0, column=1, sticky="ne")

    def init_control_bar(self):
        self.control_bar = CTkFrame(self)

        self.control_bar.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.control_bar.grid_rowconfigure(0, weight=1)

        self.size_str = StringVar()
        self.size_str.set("")
        self.size_entry = CTkEntry(self.control_bar, textvariable=self.size_str)
        self.size_entry.configure(validate='all', validatecommand=(self.register(self.size_validate), '%P', '%V'))
        self.size_entry.grid(row=0, column=0, sticky="nse")
        self.size_button = CTkButton(self.control_bar, text="Поставить размер", command=self.set_new_size)
        self.size_button.grid(row=0, column=1, sticky="nsw")

        self.load_button = CTkButton(self.control_bar, text="Загрузить", command=self.load_from_file)
        self.load_button.grid(row=0, column=2, sticky="nse")
        self.save_button = CTkButton(self.control_bar, text="Сохранить", command=self.save_to_file)
        self.save_button.grid(row=0, column=3, sticky="nsw")

    def size_validate(self, value, state):
        print(state)
        size_str: str = value
        print(size_str)
        if size_str == "":
            return True
        if not size_str.isnumeric():
            return False
        return True

    def set_new_size(self):
        pass

    def save_to_file(self):
        file = filedialog.asksaveasfile()
        self.filepath = file.name
        print(self.filepath)
        pass

    def load_from_file(self):
        filepath = filedialog.askopenfile()
        self.filepath = filepath.name
        print(self.filepath)
        pass

