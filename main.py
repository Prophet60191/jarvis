import tkinter as tk
from random import choice

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.color_button = tk.Button(self)
        self.color_button["text"] = "Change Color"
        self.color_button["command"] = self.change_color
        self.color_button.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def change_color(self):
        color = choice(["red", "green", "blue"])
        self.color_button["bg"] = color

root = tk.Tk()
app = Application(master=root)
app.mainloop()
