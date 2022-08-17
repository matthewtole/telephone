from os import path
import random
import uuid
import logging
from time import time
from os.path import join
from typing import Optional
from config import MESSAGES_DIR, DATABASE_FILE
from database import Database

from audio.player import AudioPlayer
from audio.recorder import AudioRecorder
from button import Button
from audio_track import AudioTrack, DIGIT_TRACKS


class Task:
    """
    Base class for all Tasks
    """

    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)
        pass

    def tick(self) -> None:
        pass

    def start(self) -> None:
        pass

    def is_complete(self) -> bool:
        return True

    def stop(self) -> None:
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

    def stop(self) -> None:
        self.task.stop() if self.task is not None else None

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

    def stop(self) -> None:
        self._end_time = time()

    def reset(self) -> None:
        self._end_time = -1


class TaskAudio(Task):
    """
    Base class for Tasks that play audio files.
    """

    def __init__(self, audio_player=AudioPlayer()) -> None:
        super().__init__()
        self._audio_player = audio_player
        self._has_played = False

    def start(self) -> None:
        self._has_played = True

    def tick(self) -> None:
        super().tick()
        self._audio_player.tick()

    def is_complete(self) -> bool:
        self.tick()
        return not self._audio_player.is_playing and self._has_played is True

    def stop(self) -> None:
        super().stop()
        self._audio_player.stop()

    def reset(self):
        super().stop()
        self._has_played = False


class TaskAudioTrack(TaskAudio):
    def __init__(self, track: AudioTrack, audio_player=AudioPlayer()) -> None:
        super().__init__(audio_player)
        self.track = track

    def start(self) -> None:
        super().start()
        self._audio_player.play(join("audio", self.track.value))


class TaskChoice(Task):
    def __init__(self) -> None:
        super().__init__()
        self.choice: Optional[int] = None

    def on_button(self, button: Button):
        self.choice = button.value

    def is_complete(self) -> bool:
        return self.choice is not None

    def stop(self) -> None:
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

    def stop(self) -> None:
        for task in self.sub_tasks:
            if not task.is_complete():
                task.stop()

    def reset(self):
        self.stop()
        for task in self.sub_tasks:
            task.reset()


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
            self.stop()
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
            self.log.info("Starting %s" % self.task.__class__.__name__)

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
            task.stop()
            task.reset()
        self.index = 0


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

    def stop(self) -> None:
        self.code = []
        super().stop()

    def code_string(self) -> str:
        return "".join(map(lambda c: str(c), self.code))

    def reset(self):
        self.code_completed = False
        self.code = []


class TaskLoop(TaskRunTask):
    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task

    def tick(self) -> None:
        super().tick()
        if self.task.is_complete():
            self.reset()
            self.start()

    def is_complete(self) -> bool:
        return self.task is None

    def stop(self) -> None:
        super().stop()
        self.task = None


class TaskAudioSequence(TaskSequence):
    """
    Task for reading out a sequence of numbers using an AudioPlayer.
    """

    def __init__(self, code: str, audio_player=AudioPlayer()) -> None:
        super().__init__(
            list(map(lambda c: TaskAudioTrack(DIGIT_TRACKS[c], audio_player), code))
        )


class TaskRecord(Task):
    def __init__(
        self, filename: str, end_button=Button.STAR, audio_recorder=AudioRecorder()
    ) -> None:
        super().__init__()
        self._audio_recorder = audio_recorder
        self._filename = filename
        self._is_complete = False
        self._end_button = end_button

    def start(self):
        self._audio_recorder.start()

    def tick(self):
        self._audio_recorder.tick()

    def on_button(self, button: Button) -> None:
        if button == self._end_button:
            self._audio_recorder.stop()
            self._audio_recorder.save(self._filename)
            self._is_complete = True

    def stop(self) -> None:
        self._audio_recorder.stop()

    def is_complete(self) -> bool:
        return self._is_complete

    def reset(self):
        self.stop()
        self._audio_recorder.reset()
        self._is_complete = False


class TaskRecordMessage(TaskRunTask):
    def __init__(self, audio_recorder=AudioRecorder(), DB=Database) -> None:
        super().__init__()
        self._audio_recorder = audio_recorder
        self._DB = DB
        self.setup()

    def setup(self):
        self._filename = "%s.wav" % uuid.uuid4().hex
        self.task = TaskRecord(
            path.join(MESSAGES_DIR, self._filename), audio_recorder=self._audio_recorder
        )
        self._messaged_saved = False

    def tick(self):
        super().tick()
        if self.task.is_complete():
            self._DB(DATABASE_FILE).messages.insert(self._filename, 0)
            self._messaged_saved = True

    def is_complete(self) -> bool:
        return super().is_complete() and self._messaged_saved

    def reset(self) -> None:
        self.setup()
        return super().reset()


class TaskPlayback(TaskAudio):
    def __init__(self, filename: str, audio_player=AudioPlayer()) -> None:
        super().__init__(audio_player)
        self._filename = filename

    def start(self) -> None:
        super().start()
        self._audio_player.play(self._filename)


class TaskPlayMessage(TaskRunTask):
    def __init__(self, audio_player=AudioPlayer()) -> None:
        super().__init__()
        self._audio_player = audio_player

    def start(self) -> None:
        db = Database(DATABASE_FILE)
        if db.messages.count() <= 0:
            raise Exception("Could not find a message to play")

        count = 0
        while count < 100:
            messages = db.messages.list_with_play_count(count)
            if len(messages) > 0:
                message = random.choice(messages)
                self.task = TaskPlayback(
                    join(MESSAGES_DIR, message.filename), self._audio_player
                )
                db.messages.play(message.id)
                super().start()
                break
            count += 1

        db.connection.close()


class TaskDecisionTree(TaskRunTask):
    def __init__(
        self,
        tree: dict[int, Task],
    ) -> None:
        super().__init__()
        self._tree = tree
        self.task = TaskChoice()
        self.has_chosen = False

    def tick(self) -> None:
        super().tick()
        if not self.has_chosen and self.task.is_complete():
            choice = self.task.choice
            self.task = self._tree.get(self.task.choice)
            if self.task is None:
                self.log.warn("Invalid choice %d" % choice)
            else:
                self.has_chosen = True
                self.task.start()

    def is_complete(self) -> bool:
        if self.task is None:
            return False
        return self.has_chosen and self.task.is_complete()

    def reset(self) -> None:
        super().reset()
        self.has_chosen = False
        self.task = TaskChoice()
