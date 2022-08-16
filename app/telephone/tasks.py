from enum import Enum
from time import time
from os.path import join
import logging

from audio.player import AudioPlayer
from .button import Button


class AudioTrack(Enum):
    INTRO = "intro-01.wav"
    # DIGIT_0 = "digits/0.wav"
    DIGIT_1 = "digits/1.wav"
    DIGIT_2 = "digits/2.wav"
    DIGIT_3 = "digits/3.wav"
    DIGIT_4 = "digits/4.wav"
    DIGIT_5 = "digits/5.wav"
    DIGIT_6 = "digits/6.wav"
    DIGIT_7 = "digits/7.wav"
    DIGIT_8 = "digits/8.wav"
    DIGIT_9 = "digits/8.wav"


class Task:
    """
    Base class for all Tasks
    """

    def __init__(self) -> None:
        pass

    def tick(self) -> None:
        pass

    def start(self) -> None:
        pass

    def is_complete(self) -> bool:
        self.tick()  # TODO: Figure out if we need this
        return True

    def abort(self) -> None:
        pass

    def on_button(self, button: Button) -> None:
        pass

    def reset(self) -> None:
        pass


class TaskRunTask(Task):
    """
    Base class for any task that runs a sub-task (or a sequence of tasks).

    Attributes
    ----------
    task : Optional[Task]
        The task that is currently being run.
    """

    def __init__(self) -> None:
        super().__init__()
        self.task = None

    def tick(self) -> None:
        self.task.tick() if self.task is not None else None

    def start(self) -> None:
        self.task.start() if self.task is not None else None

    def is_complete(self) -> bool:
        return self.task.is_complete() if self.task is not None else False

    def abort(self) -> None:
        self.task.abort() if self.task is not None else None

    def on_button(self, button: Button) -> None:
        self.task.on_button(button) if self.task is not None else None

    def reset(self) -> None:
        self.task.reset() if self.task is not None else None


class TaskWait(Task):
    """
    Task that waits for a number of seconds.

    Attributes
    ----------
    duration : float
        Number of seconds to wait for
    """

    def __init__(self, duration: float) -> None:
        super().__init__()
        self.duration = duration
        self._end_time = -1

    def start(self) -> None:
        self._end_time = time() + self.duration

    def is_complete(self) -> bool:
        self.tick()
        return self._end_time > 0 and time() >= self._end_time

    def abort(self) -> None:
        self._end_time = time()

    def __repr__(self) -> str:
        return "TaskWait(%f)" % (self.duration)

    def reset(self) -> None:
        self.start()


class TaskAudio(Task):
    def __init__(self, audio_player=AudioPlayer()) -> None:
        super().__init__()
        self._audio_player = audio_player

    def tick(self) -> None:
        super().tick()
        self._audio_player.tick()

    def abort(self) -> None:
        super().abort()
        self._audio_player.stop()


class TaskAudioSequence(TaskAudio):
    """
    Task for reading out a sequence of numbers using an AudioPlayer.
    """

    DIGIT_TRACKS = {
        "1": AudioTrack.DIGIT_1,
        "2": AudioTrack.DIGIT_2,
        "3": AudioTrack.DIGIT_3,
        "4": AudioTrack.DIGIT_4,
        "5": AudioTrack.DIGIT_5,
        "6": AudioTrack.DIGIT_6,
        "7": AudioTrack.DIGIT_7,
        "8": AudioTrack.DIGIT_8,
        "9": AudioTrack.DIGIT_9,
    }

    def __init__(self, code: str, audio_player=AudioPlayer()) -> None:
        super().__init__(audio_player=audio_player)
        self._log = logging.getLogger("TaskAudioSequence")
        self._code = code
        self._index = 0

    def _play_next_track(self) -> None:
        track = TaskAudioSequence.DIGIT_TRACKS[self._code[self._index]]
        if track is None:
            self._log.error("Could not find track for '%s'" % self._code[self._index])
            return

        self._audio_player.play(join("../audio", track.value))

    def start(self) -> None:
        super().start()
        self._play_next_track()

    def tick(self) -> None:
        super().tick()
        self._audio_player.tick()
        if not self._audio_player.is_playing:
            self._index = self._index + 1
            if self._index < len(self._code):
                self._play_next_track()

    def is_complete(self) -> bool:
        return self._index >= len(self._code) and not self._audio_player.is_playing

    def reset(self) -> None:
        self._audio_player.stop()
        self._index = 0
        self.start()


class TaskAudioTrack(TaskAudio):
    def __init__(self, track: AudioTrack, audio_player=AudioPlayer()) -> None:
        super().__init__(audio_player)
        self.track = track
        self.has_played = False

    def start(self) -> None:
        self.has_played = True
        self._audio_player.play(join("../audio", self.track.value))

    def is_complete(self) -> bool:
        self.tick()
        return not self._audio_player.is_playing and self.has_played is True

    def reset(self):
        self._audio_player.stop()
        self.start()


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

    def reset(self) -> None:
        self.choice = None


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

    def reset(self):
        self.abort()
        for task in self.sub_tasks:
            task.reset()
        self.start()


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


class TaskSequence(TaskRunTask):
    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self.tasks = tasks
        self.index = 0

    def start_next_task(self):
        if self.index < len(self.tasks):
            self.task = self.tasks[self.index]
            self.task.start()

    def start(self):
        self.start_next_task()

    def tick(self):
        super().tick()
        if self.task is not None and self.task.is_complete():
            self.index += 1
            self.start_next_task()

    def is_complete(self) -> bool:
        self.tick()
        if self.task is None:
            return False
        return self.task.is_complete() and self.index >= len(self.tasks)

    def reset(self):
        for task in self.tasks:
            task.abort()
            task.reset()
        self.index = 0
        self.start()


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
        return "".join(map(lambda c: str(c), self.code))

    def reset(self):
        self.code_completed = False
        self.code = []
        self.start()


class TaskLoop(TaskRunTask):
    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task

    def tick(self) -> None:
        super().tick()
        if self.task.is_complete():
            self.reset()

    def is_complete(self) -> bool:
        return self.task is None

    def abort(self) -> None:
        super().abort()
        self.task = None
