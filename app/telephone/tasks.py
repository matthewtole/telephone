from enum import Enum
from time import time
from os.path import join

from audio.player import AudioPlayer


class AudioTrack(Enum):
    INTRO = "intro-01.wav"


class Button(Enum):
    NUM_0 = 0
    NUM_1 = 1
    NUM_2 = 2
    NUM_3 = 3
    NUM_4 = 4
    NUM_5 = 5
    NUM_6 = 6
    NUM_7 = 7
    NUM_8 = 8
    NUM_9 = 9

    STAR = 100
    POUND = 101


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
    def __init__(self, duration: float) -> None:
        super().__init__()
        self.duration = duration
        self.end_time = -1

    def start(self) -> None:
        self.end_time = time() + self.duration

    def is_complete(self) -> bool:
        return self.end_time > 0 and time() >= self.end_time

    def abort(self) -> None:
        self.end_time = time()

    def __repr__(self) -> str:
        return "TaskWait(%f)" % (self.duration)


class TaskAudio(Task):
    def __init__(self, track: AudioTrack, audio_player=AudioPlayer()) -> None:
        super().__init__()
        self.track = track
        self.audio_player = audio_player
        self.has_played = False

    def start(self) -> None:
        self.has_played = True
        self.audio_player.play(join('../audio', self.track.value))

    def tick(self) -> None:
        self.audio_player.tick()

    def is_complete(self) -> bool:
        return not self.audio_player.is_playing and self.has_played == True

    def abort(self) -> None:
        return self.audio_player.stop()

    def __repr__(self) -> str:
        return "TaskWait(%s)" % (self.track.value)


class TaskChoice(Task):
    def __init__(self) -> None:
        super().__init__()
        self.choice = None

    def on_button(self, button: Button):
        self.choice = button.value

    def is_complete(self) -> bool:
        return self.choice is not None

    def abort(self) -> None:
        self.choice = -1


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
            if not task.is_complete():
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


class TaskSequence(Task):
    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self.tasks = tasks
        self.current_task = None

    def start(self):
        self.current_task = self.tasks.pop(0)
        self.current_task.start()

    def tick(self):
        if self.current_task is not None:
            self.current_task.tick()
            if self.current_task.is_complete() and len(self.tasks) > 0:
                self.current_task = self.tasks.pop()
                self.current_task.start()

    def is_complete(self) -> bool:
        self.tick()
        if self.current_task is None:
            return False
        return self.current_task.is_complete() and len(self.tasks) == 0

    def abort(self) -> None:
        if self.current_task is not None:
            self.current_task.abort()


class TaskCode(Task):
    def __init__(self) -> None:
        super().__init__()
        self.code = []
        self.code_completed = False

    def is_complete(self) -> bool:
        return self.code_completed

    def on_button(self, button: Button) -> None:
        if button == Button.POUND:
            self.code_completed = True
        elif button.value < 100:
            self.code.append(button.value)

    def abort(self) -> None:
        self.code = []
        super().abort()

    def code_string(self) -> str:
        return ''.join(map(lambda c: str(c), self.code))
