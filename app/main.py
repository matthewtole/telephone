import logging
import os
from threading import Thread
from audio_track import AudioTrack
from input_manager import DesktopInputManager
from telephone import Telephone
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


if __name__ == "__main__":
    setup()
    db = Database(DATABSE_FILE)
    db.create_tables()
    db.connection.close()

    root_task = tasks.TaskSequence(
        [
            tasks.TaskAudioTrack(AudioTrack.INTRO),
            tasks.TaskLoop(
                tasks.TaskSequence(
                    [
                        tasks.TaskAudioTrack(AudioTrack.MENU_1),
                        tasks.TaskDecisionTree(
                            {
                                1: tasks.TaskSequence(
                                    [
                                        tasks.TaskAudioTrack(AudioTrack.RECORD_INTRO),
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.BEEP),
                                        tasks.TaskRecordMessage(),
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.RECORD_OUTRO),
                                    ]
                                ),
                                2: tasks.TaskPlayMessage(),
                            }
                        ),
                        tasks.TaskWait(1),
                    ]
                )
            ),
        ]
    )

    desktop = DesktopInputManager()
    phone = Telephone(desktop, root_task, loop=True)

    phone_thread = Thread(target=phone.start)
    phone_thread.start()
    desktop.start()
