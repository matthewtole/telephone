from enum import Enum
from time import time
from os.path import join
import logging
from audio.player import AudioPlayer


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
        self.tick()  # TODO: Figure out if we need this
        return True

    def abort(self) -> None:
        pass

    def on_button(self, button: Button) -> None:
        pass


class TaskWait(Task):
    def __init__(self, duration: float) -> None:
        super().__init__()
        self.duration = duration
        self.end_time = -1

    def start(self) -> None:
        self.end_time = time() + self.duration

    def is_complete(self) -> bool:
        self.tick()
        return self.end_time > 0 and time() >= self.end_time

    def abort(self) -> None:
        self.end_time = time()

    def __repr__(self) -> str:
        return "TaskWait(%f)" % (self.duration)


class TaskAudioSequence(Task):
    DIGIT_TRACKS = {
        '1': AudioTrack.DIGIT_1,
        '2': AudioTrack.DIGIT_2,
        '3': AudioTrack.DIGIT_3,
        '4': AudioTrack.DIGIT_4,
        '5': AudioTrack.DIGIT_5,
        '6': AudioTrack.DIGIT_6,
        '7': AudioTrack.DIGIT_7,
        '8': AudioTrack.DIGIT_8,
        '9': AudioTrack.DIGIT_9,
    }

    def __init__(self, code: str, audio_player=AudioPlayer()) -> None:
        super().__init__()
        self.log = logging.getLogger("TaskAudioSequence")
        self.code = code
        self.index = 0
        self.audio_player = audio_player

    def play_next_track(self) -> None:
        track = TaskAudioSequence.DIGIT_TRACKS[self.code[self.index]]
        if track is None:
            self.log.error("Could not find track for '%s'" % self.code[self.index])
            return

        self.audio_player.play(join('../audio', track.value))

    def start(self) -> None:
        super().start()
        self.play_next_track()

    def tick(self) -> None:
        super().tick()
        self.audio_player.tick()
        if not self.audio_player.is_playing:
            self.index = self.index + 1
            if self.index < len(self.code):
                self.play_next_track()

    def is_complete(self) -> bool:
        return self.index >= len(self.code) and not self.audio_player.is_playing


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
        self.tick()
        return not self.audio_player.is_playing and self.has_played is True

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

    def on_button(self, button: Button):
        self.current_task.on_button(button)


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


class TaskDemoCode(Task):
    def __init__(self) -> None:
        super().__init__()
        self.code_task = TaskCode()
        self.audio_task = None

    def start(self) -> None:
        self.code_task.start()

    def on_button(self, button: Button) -> None:
        super().on_button(button)
        self.code_task.on_button(button)

    def tick(self) -> None:
        if not self.code_task.is_complete():
            self.code_task.tick()
        elif self.audio_task is None:
            self.audio_task = TaskAudioSequence(self.code_task.code_string())
            self.audio_task.start()
        elif not self.audio_task.is_complete():
            self.audio_task.tick()

    def is_complete(self) -> bool:
        return self.code_task.is_complete() and self.audio_task is not None and self.audio_task.is_complete()