from typing import Optional

from pynput import keyboard
from enum import Enum


class Button(Enum):
    NUM_0 = 0,
    NUM_1 = 1,
    NUM_2 = 2,
    NUM_3 = 3,
    NUM_4 = 4,
    NUM_5 = 5,
    NUM_6 = 6,
    NUM_7 = 7,
    NUM_8 = 8,
    NUM_9 = 9,
    STAR = 10,
    POUND = 11,
    MIDDLE_UPPER = 12,
    MIDDLE_LOWER = 13,
    CRADLE = 14


class Input:
    def __init__(self) -> None:
        self.button: Optional[Button] = None

    def button_pressed(self) -> Optional[Button]:
        tmp = self.button
        self.button = None
        return tmp


class PhoneInput(Input):
    def __init__(self) -> None:
        super().__init__()


class KeyboardInput(Input):
    KEY_MAPPINGS = {
        '0': Button.NUM_0,
        '1': Button.NUM_1,
        '2': Button.NUM_2,
        '3': Button.NUM_3,
        '4': Button.NUM_4,
        '5': Button.NUM_5,
        '6': Button.NUM_6,
        '7': Button.NUM_7,
        '8': Button.NUM_8,
        '9': Button.NUM_9,
        'q': Button.CRADLE,
        'z': Button.STAR,
        'x': Button.POUND,
    }

    def __init__(self) -> None:

        super().__init__()

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()

    def on_press(self, key):
        try:
            self.button = KeyboardInput.KEY_MAPPINGS.get(key.char, None)
        except AttributeError:
            pass

    def on_release(self, key):
        pass
