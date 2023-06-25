import time
from gpiozero import InputDevice, OutputDevice
from abc import abstractmethod
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
            [None, None, None, None],
            [Button.NUM_3, Button.NUM_9, Button.NUM_6, Button.NUM_0],
            [Button.NUM_2, Button.NUM_8, Button.NUM_5, Button.STAR],
            [Button.NUM_1, Button.NUM_7, Button.NUM_4, Button.POUND],
        ]

        self._pressed = set([])

    def start(self) -> None:
        self._inputs = list(
            map(lambda pin: InputDevice(pin, pull_up=True), self._input_pins)
        )
        self._outputs = list(
            map(lambda pin: InputDevice(pin, pull_up=True), self._output_pins)
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
                time.sleep(0.05)

    def button_pressed(self):
        b = self.last_button
        self.last_button = None
        return b

    def is_handset_up(self) -> bool:
        return True

    def stop(self) -> None:
        self.is_running = False
