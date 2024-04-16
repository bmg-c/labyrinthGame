import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from math import sin,cos
import numpy as np

FUNCTIONS = {
    "x^2-2": lambda x: x ** (2)-2,
    "x^3": lambda x: x ** 3,
    "sin(x)": lambda x: sin(x)
}

DFUNCTIONS = {
    "x^2-2": lambda x: 2*x ,
    "x^3": lambda x: 3*x ** 2,
    "sin(x)": lambda x: cos(x)
}
#  Функция для вычисления коэффициентов параболы
def get_coefficients(x1, y1, x2, y2, x3, y3):
    # Вычисляем знаменатель
    denom = (x1-x2) * (x1-x3) * (x2-x3)
    # Вычисляем коэффициенты
    A     = (x3 * (y2-y1) + x2 * (y1-y3) + x1 * (y3-y2)) / denom
    B     = (x3*x3 * (y1-y2) + x2*x2 * (y3-y1) + x1*x1 * (y2-y3)) / denom
    C     = (x2 * x3 * (x2-x3) * y1+x3 * x1 * (x3-x1) * y2+x1 * x2 * (x1-x2) * y3) / denom

    return A,B,C

# Функция параболы
def parabola(x, a, b, c):
    return a * x**2 + b * x + c  

# Функция для получения массивов значений x и y
def get_values(a, b, n, f):
    h = (b - a) / n
    x_values = [a + i*h/2 for i in range(2*n+1)]
    y_values = [f(x) for x in x_values]
    return x_values, y_values

# Функция для получения равномерно распределенных значений на [a,b]
def linspace(a, b, n):
    h = (b - a) / n
    return [a + i*h for i in range(n+1)]

class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Метод касательных")
        self.window.minsize(900,650)

        self.create_menubar()
        self.create_left_panel()
        self.create_main_panel()
        self.create_bottom_panel()
        self.FUNCTIONS = FUNCTIONS
        self.DFUNCTIONS = DFUNCTIONS

    
    def create_menubar(self):
        menubar = tk.Menu(self.window)

        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Настройки", command=self.help)
        file_menu.add_separator()
        file_menu.add_command(label="Выход",command=self.window.quit)
        help_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе...", command=self.help)

        self.window.config(menu=menubar)


    def create_left_panel(self):
        left_panel = ttk.Frame(self.window)
        left_panel.pack(side=tk.LEFT,anchor=tk.N, padx=20, pady=10)
        
        parameters_frame = ttk.Frame(left_panel)
        parameters_frame.pack(pady=10, anchor="w")
        parameters_frame.configure(borderwidth=2, relief="solid", padding= (20, 20, 20, 20))
        # self.function_options = ttk.Combobox(parameters_frame, values=["x^2-2", "x^3", "sin(x)"], state="readonly")
        # self.function_options.set("x^2-2")
        # self.function_options.pack(pady=10)

        
        params_label = ttk.Label(parameters_frame, text="Параметры", font=("Candara", 14))
        params_label.pack(pady=(0,20))

        function_label = ttk.Label(parameters_frame, text="Выберите функцию", font=("Candara", 12))
        function_label.pack()

        self.function_options = ttk.Combobox(parameters_frame, values=["x^2-2", "x^3", "sin(x)"], state="readonly")
        self.function_options.set("x^2-2")
        self.function_options.pack(pady=10)

        a_frame = ttk.Frame(parameters_frame)
        a_frame.pack(pady=10, anchor="w")
        b_frame = ttk.Frame(parameters_frame)
        b_frame.pack(pady=10, anchor="w")

        a_label = ttk.Label(a_frame, text="a = ")
        a_label.pack(side=tk.LEFT)

        self.a_entry = ttk.Entry(a_frame, width=16)
        self.a_entry.insert(0, 0)
        self.a_entry.pack(side=tk.LEFT)

        b_label = ttk.Label(b_frame, text="b = ")
        b_label.pack(side=tk.LEFT)

        self.b_entry = ttk.Entry(b_frame, width=16)
        self.b_entry.insert(0, 10)
        self.b_entry.pack(side=tk.LEFT)

        accuracy_label = ttk.Label(parameters_frame, text="Выберите точность",font=("Candara", 12))
        accuracy_label.pack()

        self.accuracy_options = ttk.Combobox(parameters_frame, values=[0.01, 0.001, 0.0001], state="readonly")
        self.accuracy_options.set(0.0001)
        self.accuracy_options.pack(pady=10)

        buttom_frame = ttk.Frame(left_panel)
        buttom_frame.pack(pady=10, anchor="w")
        show_button = ttk.Button(buttom_frame, text="Решить",  command=self.show_graph)
        show_button.pack(side=tk.LEFT,padx=5)
        clear_button = ttk.Button(buttom_frame, text="Очистить",  command=self.clear_parameters)
        clear_button.pack(side=tk.LEFT)
        results_frame = ttk.Frame(left_panel)
        results_frame.pack(pady=10, anchor="w")
        results_frame.configure(borderwidth=2, relief="solid", padding= (20, 20, 20, 20))
        self.result_label = ttk.Label(results_frame, text="Результат", font=("Candara", 14))
        self.result_label.pack(pady=(0,20))
        partitions_frame = ttk.Frame(results_frame)
        partitions_frame.pack(pady=5, anchor="w")
        # partitionsText_label = ttk.Label(partitions_frame, text="Кол-во разбиений = ",font=("Candara", 12))
        # partitionsText_label.pack(side=tk.LEFT)
        # self.partitions_label = ttk.Label(partitions_frame, text="")
        # self.partitions_label.pack(side=tk.LEFT)
        integral_frame = ttk.Frame(results_frame)
        integral_frame.pack(pady=5, anchor="w")
        integralText_label = ttk.Label(integral_frame, text="Приближенное значение x = ",font=("Candara", 12))
        integralText_label.pack(side=tk.LEFT)
        self.integral_label = ttk.Label(integral_frame, text="")
        self.integral_label.pack(side=tk.LEFT)
        


    def create_main_panel(self):
        main_panel = ttk.Frame(self.window)
        main_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)
        # btn = ttk.Button(self, text="Показать график", command=self.show_plot_in_new_window)
        # btn.pack(pady=10)
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, main_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top",fill='both',expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, main_panel)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", fill='both', expand=1)
        
    def show_plot_in_new_window(self):
        new_window = tk.Toplevel(self.window)
        new_window.title("График")
        new_canvas = FigureCanvasTkAgg(self.figure, new_window)
        new_canvas.draw()
        new_canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, new_window)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", fill='both', expand=1)

    def create_bottom_panel(self):
        bottom_panel = ttk.Frame(self.window)
        bottom_panel.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        button_frame = ttk.Frame(bottom_panel)
        button_frame.pack(pady=10)

        self.previous_button = ttk.Button(button_frame, text="Назад", command=self.previous_step, state="disabled")
        self.previous_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(button_frame, text="Вперед", command=self.next_step, state="disabled")
        self.next_button.pack(side=tk.LEFT, padx=5)

        # self.final_button = ttk.Button(button_frame, text="Итог", command=self.show_plot_in_new_window)
        # self.final_button.pack(side=tk.LEFT,padx=5)
    # Функция определяет начальное приближение
    def choose_initial_guess(self, a, b, f):
        c = a - ((b-a)*f(a))/(f(b)-f(a))
        if f(a)*f(c) < 0:
            return a
        elif f(a) * f(c) > 0:
            return b
        else:
            return c
                

    def tangent_method(self, a, b, eps, f, df):
        x0 = self.choose_initial_guess(a, b, f)
        while True:
            x1 = x0 - f(x0) / df(x0)
            self.xs.append(x1)
            self.ys.append(f(x1))
            if abs(x1 - x0) < eps:
                return x1
            x0 = x1
        

    def visualize(self, a, b, f, df, i):
        # self.ax.clear()
        
        m = df(self.xs[i])
        x_intersect = self.xs[i] - self.ys[i] / m
        x_tan = np.linspace(min(self.xs[i], x_intersect), max(self.xs[i], x_intersect), 400)
        y_tan = m * (x_tan - self.xs[i]) + self.ys[i]
        self.ax.plot(x_tan, y_tan)
        self.ax.plot(self.xs[i], 0, 'ro')
        self.ax.plot([self.xs[i], self.xs[i]], [0, self.ys[i]], color='black')
        self.ax.plot(self.xs[i], self.ys[i], 'ro')
        
        self.ax.set_title('Касательные')
        # Добавляем легенду
        # self.ax.legend()

        # Подпись осей
        self.ax.set_xlabel("Ось X")
        self.ax.set_ylabel("Ось Y")
        # Выводим графики на экран
        self.ax.grid(True)
        self.canvas.draw()

    def show_graph(self):
        self.ax.clear()
        self.xs = []
        self.ys = []
        self.iter = 0
        # Get the selected function
        self.f = self.FUNCTIONS.get(self.function_options.get())
        self.df = self.DFUNCTIONS.get(self.function_options.get())
        # Get the values of a and b from the input fields
        self.a = self.validate_entry(self.a_entry.get())
        self.b = self.validate_entry(self.b_entry.get())

        if self.a is None and self.b is None:
            self.a_entry.delete(0, 'end')
            self.a_entry.insert(0, 0)
            self.b_entry.delete(0, 'end')
            self.b_entry.insert(0, 10)
            messagebox.showerror("Ошибка ввода", "Введите корректное значения a и b")
            return
        if self.a is None:
            messagebox.showerror("Ошибка ввода", "Введите корректное значение a")
            self.a_entry.delete(0, 'end')
            self.a_entry.insert(0, 0)
            return
        if self.b is None:
            self.b_entry.delete(0, 'end')
            self.b_entry.insert(0, 10)
            messagebox.showerror("Ошибка ввода", "Введите корректное значение b")
            return
        # Get the accuracy from the input field
        self.eps = float(self.accuracy_options.get())

        # Define the function to integrate
        self.tangent_method(self.a,self.b,self.eps,self.f,self.df)
        if self.xs:
            self.result_label.configure(text="Текущий результат", font=("Candara", 14))
            self.showStepByStep()
            func_values = get_values(self.a,self.b,100,self.f)
            self.ax.plot(func_values[0], func_values[1], color='blue')

    def showStepByStep(self):
        if self.iter == 0:
            self.previous_button.configure(state="disabled")
        elif str(self.previous_button.cget("state")) == "disabled":
            self.previous_button.configure(state="normal")
        if self.iter == len(self.xs)-1:
            self.next_button.configure(state="disabled")
            # self.final_button.configure(state="disabled")
            self.result_label.configure(text="Итоговый результат", font=("Candara", 14))  
        elif str(self.next_button.cget("state")) == "disabled":
            self.next_button.configure(state="normal")
            # self.final_button.configure(state="normal")
            self.result_label.configure(text="Текущий результат", font=("Candara", 14))
        self.visualize (self.a,self.b,self.f,self.df,self.iter)
        # integralFormat = str(self.results[self.iter]).split('.')
        self.integral_label.configure(text="{0:.3}".format(self.xs[self.iter]))
        # self.partitions_label.configure(text=n)

    def validate_entry(self, value):
        try:
            return float(value)
        except ValueError:
            return None
    
    def next_step(self):
        self.iter += 1
        self.showStepByStep()

    def previous_step(self):
        self.iter -= 1
        self.showStepByStep()

    def final_step(self):
        self.iter = len(self.xs)-1
        self.showStepByStep()

    def help(self):
        messagebox.showinfo("Помощь", "Скоро здесь будет информация...")

    def change_theme(self):
        if self.window.call("ttk::style", "theme", "use") == "azure-dark":
            # Set light theme
            self.window.call("set_theme", "light")
        else:
            # Set dark theme
            self.window.call("set_theme", "dark")

    def clear_parameters(self):
        self.ax.clear()
        self.canvas.draw()
        self.function_options.set("sin(x)")
        self.a_entry.delete(0, 'end')
        self.a_entry.insert(0, 0)
        self.b_entry.delete(0, 'end')
        self.b_entry.insert(0, 10)
        self.accuracy_options.set(0.0001)
        self.result_label.configure(text="Результат", font=("Candara", 14)) 
        self.integral_label.configure(text='')
        # self.partitions_label.configure(text='')

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()