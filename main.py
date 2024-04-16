from customtkinter import *
from customtkinter import CTkFrame
from maze import Maze
from tkinter import Event


class MazeFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=700, height=700)

        self.maze = Maze(10, 10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.bind("<B1-Motion>", self.hello)

    def hello(self, event: Event):
        print(str(event.x) + " " + str(event.y))


class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("Maze")
        # self.resizable(False, False)
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
            msg = "Размер лабиринта должен быть не меньше 5 и iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiне больше 20"
        if error:
            self.info_label.configure(text=msg)
            return
        # self.maze = Maze(1, 1)

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
