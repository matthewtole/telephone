import logging
import os
from threading import Thread
from telephone.gui import Telephone, Gui
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
    task = telephone.tasks.TaskSequence([
        telephone.tasks.TaskChoice(),
        telephone.tasks.TaskAudio(telephone.tasks.AudioTrack.INTRO)
    ])

    gui = Gui()
    tel = Telephone(gui, task)
    btn_thrad = Thread(target=tel.start)
    btn_thrad.start()
    gui.start()
