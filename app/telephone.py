from time import sleep
from tasks import Task
from input_manager import InputManager
from typing import Callable


class Telephone:
    def __init__(self, input_manager: InputManager, task: Callable[..., Task]) -> None:
        self.input_manager = input_manager
        self.task_fn = task
        self.task = self.task_fn()

    def start(self):
        while self.input_manager.is_running:
            if self.input_manager.is_handset_up():
                self.task.start()
            else:
                continue

            while not self.task.is_complete():
                if not self.input_manager.is_handset_up():
                    print("STOP")
                    self.task.stop()
                    self.task.reset()
                    break

                self.task.tick()

                button = self.input_manager.button_pressed()
                if button is not None:
                    self.task.on_button(button)

                sleep(0.1)

            sleep(0.1)

        self.input_manager.stop()
        self.task.stop()
