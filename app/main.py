import logging
import os
from threading import Thread
from audio_track import AudioTrack
from input_manager import DesktopInputManager
from telephone import Telephone
from button import Button
import tasks

from config import DATABSE_FILE, LOG_FILE, TEMP_DIR

from database import Database


def setup():
    logging.basicConfig(
        level=logging.DEBUG,
        filename=LOG_FILE,
        encoding="utf-8",
        format="%(asctime)s|%(levelname)s|%(name)s|%(message)s",
    )

    try:
        os.mkdir(TEMP_DIR)
    except FileExistsError:
        pass


class TaskDemoCode(tasks.Task):
    def __init__(self) -> None:
        super().__init__()
        self.code_task = tasks.TaskCode()
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
            self.audio_task = tasks.TaskAudioSequence(self.code_task.code_string())
            self.audio_task.start()
        elif not self.audio_task.is_complete():
            self.audio_task.tick()

    def is_complete(self) -> bool:
        return (
            self.code_task.is_complete()
            and self.audio_task is not None
            and self.audio_task.is_complete()
        )

    def reset(self) -> None:
        self.code_task.stop()
        self.audio_task.stop() if self.audio_task is not None else None
        self.code_task = tasks.TaskCode()
        self.audio_task = None


def task_demo_02():
    demo_file = os.path.join(TEMP_DIR, "demo.wav")
    return tasks.TaskSequence(
        [
            tasks.TaskAudioTrack(AudioTrack.LEAVE_MESSAGE),
            tasks.TaskRecord(demo_file),
            tasks.TaskWait(0.5),
            tasks.TaskPlayback(demo_file),
            tasks.TaskWait(0.5),
        ]
    )


def task_demo_03():
    """
    Demo task for testing the decision tree logic.
    """
    return tasks.TaskDecisionTree(
        {
            1: tasks.TaskAudioTrack(AudioTrack.DIGIT_1),
            2: tasks.TaskAudioTrack(AudioTrack.DIGIT_2),
            3: tasks.TaskAudioTrack(AudioTrack.DIGIT_3),
            4: tasks.TaskAudioTrack(AudioTrack.DIGIT_4),
            5: tasks.TaskAudioTrack(AudioTrack.DIGIT_5),
            6: tasks.TaskAudioTrack(AudioTrack.DIGIT_6),
            7: tasks.TaskAudioTrack(AudioTrack.DIGIT_7),
            8: tasks.TaskAudioTrack(AudioTrack.DIGIT_8),
            9: tasks.TaskAudioTrack(AudioTrack.DIGIT_9),
        }
    )


if __name__ == "__main__":
    setup()
    db = Database(DATABSE_FILE)

    root_task = TaskDemoCode()

    desktop = DesktopInputManager()
    phone = Telephone(desktop, root_task)

    phone_thread = Thread(target=phone.start)
    phone_thread.start()
    desktop.start()
