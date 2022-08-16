from abc import abstractmethod
import tkinter as tk
from tkinter import ttk
from functools import partial
from typing import Optional

from button import Button


class InputManager:
    def __init__(self) -> None:
        self.is_running = False
        self._is_handset_up = False

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def button_pressed(self) -> Optional[Button]:
        return None

    @abstractmethod
    def is_handset_up(self) -> bool:
        pass


class CircuitBoard(InputManager):
    def __init__(self) -> None:
        super().__init__()

    def start(self) -> None:
        pass

    def button_pressed(self) -> Optional[Button]:
        pass


class DesktopInputManager(InputManager):
    def create_button(self, button: Button, label: Optional[str] = None) -> tk.Button:
        return ttk.Button(
            self.root,
            text=str(button.value) if label is None else label,
            command=partial(self.set_button, button),
        )

    def __init__(self) -> None:
        super().__init__()
        self.is_running = True
        self.last_button: Optional[Button] = None

    def set_button(self, button: Button) -> None:
        self.last_button = button

    def __build_ui(self):
        self.root = tk.Tk()
        self.root.geometry("640x480")
        self.root.resizable(False, False)
        self.root.title("Telephone")

        for b in range(9):
            self.create_button(list(Button)[b + 1]).grid(column=b % 3, row=int(b / 3))

        self.create_button(Button.NUM_0).grid(column=0, row=3)
        self.create_button(Button.STAR, "*").grid(column=1, row=3)
        self.create_button(Button.POUND, "#").grid(column=2, row=3)

        self.checkbox_var = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(
            self.root,
            text="Is Handset Lifted?",
            variable=self.checkbox_var,
            onvalue=True,
            offvalue=False,
        )
        checkbox.grid(row=4, column=0, columnspan=3)

    def start(self) -> None:
        self.__build_ui()

        self.is_running = True
        self.root.mainloop()
        self.is_running = False

    def button_pressed(self):
        b = self.last_button
        self.last_button = None
        return b

    def is_handset_up(self) -> bool:
        return self.checkbox_var.val()

    def stop(self):
        self.root.quit()
