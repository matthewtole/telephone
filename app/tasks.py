from os import path
import random
import uuid
import logging
from time import time
from os.path import join
from typing import Optional, Type
from config import MESSAGES_DIR, DATABASE_FILE
from database import Database

from audio.player import AudioPlayer
from audio.recorder import AudioRecorder
from button import Button
from audio_track import AudioTrack


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
        self.log.error("stop() not implemented")
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
        self.task: Optional[Task] = Task()

    def tick(self) -> None:
        if self.task is None:
            self.log.error("Tried to tick a null task")
            return
        self.task.tick()

    def start(self) -> None:
        if self.task is None:
            self.log.error("Tried to start a null task")
            return
        self.task.start()

    def is_complete(self) -> bool:
        return self.task.is_complete()

    def stop(self) -> None:
        if self.task is None:
            self.log.error("Tried to stop a null task")
            return
        self.task.stop()

    def on_button(self, button: Button) -> None:
        self.task.on_button(button)

    def reset(self) -> None:
        if self.task is None:
            self.log.error("Tried to reset a null task")
            return
        self.task.reset()


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

    def __init__(self, path: str, audio_player: AudioPlayer = AudioPlayer()) -> None:
        super().__init__()
        self._audio_player = audio_player
        self._has_played = False
        self._path = path

    def start(self) -> None:
        self._has_played = True
        self._audio_player.play(self._path)

    def tick(self) -> None:
        super().tick()
        self._audio_player.tick()

    def is_complete(self) -> bool:
        self.tick()
        return not self._audio_player.is_playing and self._has_played is True

    def stop(self) -> None:
        super().stop()
        self.log.info("Stopping audio playback")
        self._audio_player.stop()

    def reset(self):
        super().stop()
        self._has_played = False


class TaskAudioTrack(TaskAudio):
    def __init__(
        self, track: AudioTrack, audio_player: AudioPlayer = AudioPlayer()
    ) -> None:
        super().__init__(join("audio", track.value), audio_player)


class TaskChoice(Task):
    def __init__(self) -> None:
        super().__init__()
        self.choice: Optional[int] = None

    def start(self) -> None:
        self.choice = None

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
        if self.task.is_complete():
            self.index += 1
            self.start_next_task()

    def is_complete(self) -> bool:
        self.tick()
        return self.task.is_complete() and self.index >= len(self.tasks)

    def reset(self):
        for task in self.tasks:
            task.stop()
            task.reset()
        self.index = 0


class TaskLoop(TaskRunTask):
    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task
        self._is_stopped = False

    def tick(self) -> None:
        super().tick()
        if self.task.is_complete():
            self.reset()
            self.start()

    def is_complete(self) -> bool:
        return self._is_stopped

    def stop(self) -> None:
        super().stop()
        self._is_stopped = True


class TaskRecord(Task):
    def __init__(
        self,
        filename: str,
        end_button: Button = Button.STAR,
        audio_recorder: AudioRecorder = AudioRecorder(),
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
            self._is_complete = True
            self._audio_recorder.stop()
            self._audio_recorder.save(self._filename)

    def stop(self) -> None:
        if not self._is_complete:
            self._audio_recorder.stop()
            self._audio_recorder.save(self._filename)
            self._is_complete = True

    def is_complete(self) -> bool:
        return self._is_complete

    def reset(self):
        self.stop()
        self._audio_recorder.reset()
        self._is_complete = False


class TaskRecordMessage(TaskRunTask):
    def __init__(
        self,
        audio_recorder: AudioRecorder = AudioRecorder(),
        DB: Type[Database] = Database,
    ) -> None:
        super().__init__()
        self._audio_recorder = audio_recorder
        self._DB = DB
        self.setup()
        self._start_time = 0

    def setup(self):
        self._filename = "%s.wav" % uuid.uuid4().hex
        self.task = TaskRecord(
            path.join(MESSAGES_DIR, self._filename), audio_recorder=self._audio_recorder
        )
        self._messaged_saved = False

    def start(self) -> None:
        self._start_time = time()
        super().start()

    def stop(self) -> None:
        self.task.stop()
        # TODO: Consider chopping off the end of the recording to eliminate the click
        self._save()

    def tick(self):
        super().tick()
        if self.task.is_complete() and not self._messaged_saved:
            self._save()

    def is_complete(self) -> bool:
        return super().is_complete() and self._messaged_saved

    def reset(self) -> None:
        self.setup()
        return super().reset()

    def _save(self) -> None:
        self._messaged_saved = True

        duration = time() - self._start_time
        # TODO: Don't save messages under X seconds long
        self._DB(DATABASE_FILE).messages.insert(self._filename, int(duration))


class TaskPlayMessage(TaskRunTask):
    def __init__(self, audio_player: AudioPlayer = AudioPlayer()) -> None:
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
                self.task = TaskAudio(
                    join(MESSAGES_DIR, message.filename), self._audio_player
                )
                db.messages.play(message.id)
                db.plays.insert(message.id)
                super().start()
                break
            count += 1

        db.connection.close()


class TaskDecisionTree(TaskRunTask):
    def __init__(
        self, tree: dict[int, Task], intro_task: Task, timeout: int = 10
    ) -> None:
        super().__init__()
        self._tree = tree
        self.task = TaskChoice()
        self.has_chosen = False
        self._end_time = -1
        self._timeout = timeout
        self._intro_task = intro_task

    def start(self) -> None:
        self._end_time = time() + self._timeout
        self._intro_task.start()

    def tick(self) -> None:
        super().tick()

        self._intro_task.tick()

        if (
            not self.has_chosen
            and self.task.is_complete()
            and self.task.__class__ == TaskChoice
        ):
            choice: int = self.task.choice  # type: ignore
            self.task = self._tree.get(choice)
            if self.task is None:
                self.log.warn("Invalid choice %d" % choice)
            else:
                self.has_chosen = True
                self._intro_task.stop()
                self.task.start()

    def is_complete(self) -> bool:
        if not self.has_chosen and self._end_time > 0 and time() >= self._end_time:
            return True
        return self.has_chosen and self.task.is_complete()

    def stop(self) -> None:
        super().stop()
        self._intro_task.stop()

    def reset(self) -> None:
        super().reset()
        self._intro_task.reset()
        self.has_chosen = False
        self.task = TaskChoice()
