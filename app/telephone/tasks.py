from enum import Enum
from time import time

from ..audio.player import AudioPlayer


class Button(Enum):
    NUM_0 = 0


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
        self.end_time = -1

    def start(self) -> None:
        self.end_time = time() + self.duration

    def is_complete(self) -> bool:
        return self.end_time > 0 and time() >= self.end_time

    def abort(self) -> None:
        self.end_time = time()


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
    pass
    # def __init__(self, emitter: events.EventEmitter) -> None:
    #     super().__init__()
    #     self.choice = None
    #     self.emitter = emitter

    # def on_button(self, button: Button):
    #     self.choice = button.value

    # def start(self) -> None:
    #     self.emitter.on('button', self.on_button)

    # def is_complete(self) -> bool:
    #     return self.choice is not None

    # def abort(self) -> None:
    #     self.choice = -1


class TaskMany(Task):
    def __init__(self, sub_tasks: list[Task]) -> None:
        super().__init__()
        self.sub_tasks = sub_tasks

    def start(self) -> None:
        for task in self.sub_tasks:
            task.start()

    def tick(self) -> None:
        for task in self.sub_tasks:
            task.tick()

    def abort(self) -> None:
        for task in self.sub_tasks:
            if not task.is_complete:
                task.abort()


class TaskAll(TaskMany):
    def is_complete(self) -> bool:
        for task in self.sub_tasks:
            if not task.is_complete():
                return False
        return True


class TaskAny(TaskMany):
    def is_complete(self) -> bool:
        has_complete_task = False
        for task in self.sub_tasks:
            if task.is_complete():
                has_complete_task = True
                break
        if has_complete_task:
            self.abort()
        return has_complete_task
