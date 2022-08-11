import logging
import os

from config import DATABSE_FILE, LOG_FILE, TEMP_DIR

from database import Database
from telephone.base import Telephone


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
    telephone = Telephone(db)
    telephone.start()
