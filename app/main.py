import logging
import os
import time
import telephone.tasks  # noqa: F401

from config import DATABSE_FILE, LOG_FILE, TEMP_DIR

from database import Database


def setup():
    logging.basicConfig(
        level=logging.DEBUG,
        filename=LOG_FILE,
        encoding='utf-8',
        format="%(asctime)s|%(levelname)s|%(name)s|%(message)s"
    )

    try:
        os.mkdir(TEMP_DIR)
    except FileExistsError:
        pass


if __name__ == "__main__":
    setup()
    db = Database(DATABSE_FILE)
    task = telephone.tasks.TaskAudio(telephone.tasks.AudioTrack.INTRO)
    task.start()
    while not task.is_complete():
        task.tick()
        time.sleep(0.1)
