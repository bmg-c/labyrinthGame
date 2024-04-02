# from tkinter import *
from tkinter import ttk, Tk

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello, world!").grid(column=0, row=0)
ttk.Button(frm, text="Print", command=lambda: print("test")).grid(column=0, row=1)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=2)

root.mainloop()
