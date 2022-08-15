import logging
import os
from threading import Thread
from telephone.input_manager import DesktopInputManager
from telephone.telephone import Telephone
import telephone.tasks

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
    root_task = telephone.tasks.TaskSequence([
        telephone.tasks.TaskDemoCode()
    ])

    desktop = DesktopInputManager()
    phone = Telephone(desktop, root_task)

    phone_thread = Thread(target=phone.start)
    phone_thread.start()
    desktop.start()
