from tkinter import *

class MyLabel(Frame):
    '''inherit from Frame to make a label with customized border'''
    def __init__(self, parent, myborderwidth=0, mybordercolor=None,
                 myborderplace='center', *args, **kwargs):
        Frame.__init__(self, parent, bg=mybordercolor)
        self.propagate(False) # prevent frame from auto-fitting to contents
        self.label = Label(self, *args, **kwargs) # make the label

        # pack label inside frame according to which side the border
        # should be on. If it's not 'left' or 'right', center the label
        # and multiply the border width by 2 to compensate
        if myborderplace == 'left':
            self.label.pack(side=RIGHT)
        elif myborderplace == 'right':
            self.label.pack(side=LEFT)
        elif myborderplace == 'bottom':
            self.label.pack(side=TOP)
        elif myborderplace == 'bottom_right':
            self.label.pack(side=TOP, anchor=NW)
        else:
            self.label.pack()
            myborderwidth = myborderwidth * 2

        # set width and height of frame according to the req width
        # and height of the label
        if myborderplace == 'bottom':
            self.config(width=self.label.winfo_reqwidth())
            self.config(height=self.label.winfo_reqheight() + myborderwidth)
        elif myborderplace == 'bottom_right':
            self.config(width=self.label.winfo_reqwidth() + myborderwidth)
            self.config(height=self.label.winfo_reqheight() + myborderwidth)
        else:
            self.config(width=self.label.winfo_reqwidth() + myborderwidth)
            self.config(height=self.label.winfo_reqheight())


root=Tk()
MyLabel(root, width=10, height=5, text='', myborderwidth=1, mybordercolor='black',
        myborderplace='bottom_right').pack()
root.mainloop()