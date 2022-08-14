
import time
from .tasks import TaskAudio, TaskChoice, TaskSequence, TaskWait
from database import Database


class Button:
    pass


demo_sequence = TaskSequence([
    TaskWait(3),
    TaskAudio("audio/intro-01.wav"),
    TaskChoice()
])


class Telephone:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.current_task = None
        self.task_queue = [demo_sequence]

    def start(self):
        while len(self.task_queue) > 0:
            self.current_task = self.task_queue.pop(0)
            self.current_task.start()
            while not self.current_task.is_complete():
                self.current_task.tick()
                time.sleep(0.1)

    def on_button(self, button: Button) -> None:
        pass
