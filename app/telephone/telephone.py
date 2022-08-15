
from time import sleep
from .tasks import Task
from .input_manager import InputManager


class Telephone:
    def __init__(self, input_manager: InputManager, task: Task) -> None:
        self.input_manager = input_manager
        self.task = task

    def start(self):
        self.task.start()

        while self.input_manager.is_running:
            if self.task.is_complete():
                break

            # if not self.input_manager.is_handset_up():
            #     # TODO: Implement me
            #     pass

            self.task.tick()

            button = self.input_manager.button_pressed()
            if button is not None:
                self.task.on_button(button)

            sleep(0.1)

        self.input_manager.stop()
        self.task.abort()
