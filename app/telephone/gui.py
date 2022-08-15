from time import sleep
import tkinter as tk
from tkinter import ttk
from threading import Thread
from functools import partial


class Gui:
    def __init__(self) -> None:
        self.is_running = True
        self.last_button = None

    def set_button(self, b: str) -> None:
        self.last_button = b

    def start(self) -> None:
        root = tk.Tk()
        root.geometry('640x480')
        root.resizable(False, False)
        root.title('Telephone')

        s = ttk.Style()
        s.configure('new.TFrame', background='#f00')

        container = ttk.Frame(root, style='new.TFrame')
        container.pack(fill=tk.BOTH, expand=1)

        for b in range(9):
            ttk.Button(
                container,
                text=str(b+1),
                command=partial(self.set_button, str(b+1))
            ).grid(
                column=b % 3,
                row=int(b/3)),

        ttk.Button(
            container,
            text="0",
            command=partial(self.set_button, "0")
        ).grid(column=0, row=3)
        ttk.Button(
            container,
            text="*",
            command=partial(self.set_button, "*")
        ).grid(column=1, row=3)
        ttk.Button(
            container,
            text="#",
            command=partial(self.set_button, "#")
        ).grid(column=2, row=3)

        self.is_running = True
        root.mainloop()
        self.is_running = False

    def button(self):
        b = self.last_button
        self.last_button = None
        return b


class ButtonListener:
    def __init__(self, gui: Gui) -> None:
        self.gui = gui

    def start(self):
        while self.gui.is_running:
            button = self.gui.button()
            if button is not None:
                print(button)
            sleep(0.1)
        print("goodbye")


gui = Gui()
btn = ButtonListener(gui)
btn_thrad = Thread(target=btn.start)
btn_thrad.start()
gui.start()
