import logging
from time import sleep
from tasks import Task
from input_manager import InputManager
from typing import Callable


class Telephone:
    def __init__(self, input_manager: InputManager, task: Callable[..., Task]) -> None:
        self.log = logging.getLogger("Telephone")
        self.input_manager = input_manager
        self.task_fn = task
        self.task = None

    def start(self):
        while self.input_manager.is_running:
            if self.task is None and self.input_manager.is_handset_up():
                self.log.info("Handset raised")
                self.task = self.task_fn()
                self.task.start()
            else:
                continue

            while not self.task.is_complete():
                if not self.input_manager.is_handset_up():
                    self.log.info("Handset lowered")
                    self.task.stop()
                    self.task = None
                    break

                self.task.tick()

                button = self.input_manager.button_pressed()
                if button is not None:
                    self.task.on_button(button)

                sleep(0.1)

            sleep(0.1)

        self.log.warn("Input manager stopped")
        self.input_manager.stop()
        self.task.stop()
