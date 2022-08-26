import time
from gpiozero import InputDevice, OutputDevice
from abc import abstractmethod
import tkinter as tk
from tkinter import ttk
from functools import partial
from typing import Any, Optional

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

    @abstractmethod
    def stop(self) -> None:
        pass


class CircuitBoard(InputManager):
    def __init__(self) -> None:
        super().__init__()
        self._output_pins = [12, 16, 20, 21]
        self._input_pins = [18, 23, 24, 25]
        self.last_button = None
        self.is_running = True

        self._mapping = [
            [Button.NUM_7, Button.NUM_9, Button.NUM_8, None],
            [Button.STAR, Button.POUND, Button.NUM_0, None],
            [Button.NUM_4, Button.NUM_6, Button.NUM_5, None],
            [Button.NUM_1, Button.NUM_3, Button.NUM_2, None],
        ]

        self._pressed = set([])

    def start(self) -> None:
        self._inputs = list(
            map(
                lambda pin: InputDevice(pin, pull_up=True),
                self._input_pins
            )
        )
        self._outputs = list(
            map(
                lambda pin: InputDevice(pin, pull_up=True),
                self._output_pins
            )
        )

        self.is_running = True

        while self.is_running:
            for o in range(4):
                self._outputs[o].close()
                tmp = OutputDevice(self._output_pins[o], active_high=False)
                tmp.on()
                for i in range(4):
                    key = self._mapping[i][o]
                    if self._inputs[i].is_active:
                        if key is None:
                            continue
                        if key not in self._pressed:
                            self._pressed.add(key)
                            self.last_button = key
                    else:
                        if key in self._pressed:
                            self._pressed.remove(key)

                tmp.close()
                self._outputs[o] = InputDevice(self._output_pins[o], pull_up=True)
                time.sleep(0.1)

    def button_pressed(self):
        b = self.last_button
        self.last_button = None
        return b

    def is_handset_up(self) -> bool:
        return True

    def stop(self) -> None:
        self.is_running = False


class DesktopInputManager(InputManager):
    def create_button(self, button: Button, label: Optional[str] = None) -> ttk.Button:
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
        return self.checkbox_var.get()

    def stop(self):
        self.root.quit()
