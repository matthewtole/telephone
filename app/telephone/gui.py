from importlib.resources import is_resource
from time import sleep
import tkinter as tk
from tkinter import ttk
from functools import partial
from typing import Optional

from .tasks import Button, Task, TaskChoice


class InputManager:
    def __init__(self) -> None:
        self.is_running = False

    def start(self) -> None:
        pass

    def button_pressed(self) -> Optional[Button]:
        return None


class Gui(InputManager):
    def __init__(self) -> None:
        super().__init__()
        self.is_running = True
        self.last_button: Optional[Button] = None

    def set_button(self, button: Button) -> None:
        self.last_button = button

    def start(self) -> None:
        self.root = tk.Tk()
        self.root.geometry('640x480')
        self.root.resizable(False, False)
        self.root.title('Telephone')

        s = ttk.Style()
        s.configure('new.TFrame', background='#f00')

        container = ttk.Frame(self.root, style='new.TFrame')
        container.pack(fill=tk.BOTH, expand=1)

        for b in range(9):
            ttk.Button(
                container,
                text=str(b+1),
                command=partial(self.set_button,  list(Button)[b+1])
            ).grid(
                column=b % 3,
                row=int(b/3)),

        ttk.Button(
            container,
            text="0",
            command=partial(self.set_button, Button.NUM_0)
        ).grid(column=0, row=3)
        ttk.Button(
            container,
            text="*",
            command=partial(self.set_button, Button.STAR)
        ).grid(column=1, row=3)
        ttk.Button(
            container,
            text="#",
            command=partial(self.set_button, Button.POUND)
        ).grid(column=2, row=3)

        self.is_running = True
        self.root.mainloop()
        self.is_running = False

    def button_pressed(self):
        b = self.last_button
        self.last_button = None
        return b

    def stop(self):
        self.root.quit()


class Telephone:
    def __init__(self, input_manager: InputManager, task: Task) -> None:
        self.input_manager = input_manager
        self.task = task

    def start(self):
        self.task.start()

        while self.input_manager.is_running:
            if self.task.is_complete():
                break

            self.task.tick()

            button = self.input_manager.button_pressed()
            if button is not None:
                self.task.on_button(button)

            sleep(0.1)

        self.input_manager.stop()
        self.task.abort()
