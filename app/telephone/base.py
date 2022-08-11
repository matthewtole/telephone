import time
from audio.player import AudioPlayer
from database import Database


class Button:
    pass


class Task:
    def __init__(self) -> None:
        pass

    def tick(self) -> None:
        pass

    def start(self) -> None:
        pass

    def is_complete(self) -> bool:
        return True

    def abort(self) -> None:
        pass


class TaskWait(Task):
    def __init__(self, duration: int) -> None:
        super().__init__()
        self.duration = duration

    def start(self) -> None:
        self.end_time = time.time() + self.duration

    def is_complete(self) -> bool:
        return time.time() >= self.end_time

    def abort(self) -> None:
        self.end_time = time.time()


class TaskAudio(Task):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename
        self.audio_player = AudioPlayer()

    def start(self) -> None:
        self.audio_player.play(self.filename)

    def tick(self) -> None:
        self.audio_player.tick()

    def is_complete(self) -> bool:
        return not self.audio_player.is_playing

    def abort(self) -> None:
        return self.audio_player.stop()


class TaskChoice(Task):
    def __init__(self, emitter) -> None:
        super().__init__()
        self.choice = None
        self.emitter = emitter

    def on_button(self, button: Button):
        self.choice = 0

    def start(self) -> None:
        self.emitter.on('button', self.on_button)

    def is_complete(self) -> bool:
        return self.choice is not None

    def abort(self) -> None:
        self.choice = -1


class Telephone:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.current_task = None
        self.task_queue = [
            TaskWait(3),
            TaskAudio("audio/intro-01.wav"),
            TaskChoice()
        ]

    def start(self):
        while len(self.task_queue) > 0:
            self.current_task = self.task_queue.pop(0)
            self.current_task.start()
            while not self.current_task.is_complete():
                self.current_task.tick()
                time.sleep(0.1)

    def on_button(self, button: Button) -> None:
        pass
