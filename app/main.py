from database import Database
from telephone import Telephone
import logging
import os

LOG_FILE = 'telephone.log'
DB_FILE = 'telephone.db'


def setup():
    logging.basicConfig(level=logging.DEBUG,
                        filename=LOG_FILE,
                        encoding='utf-8',
                        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")

    try:
        os.mkdir("temp")
    except FileExistsError:
        pass


if __name__ == "__main__":
    setup()

    db = Database(DB_FILE)
    db.create_tables()
    telephone = Telephone(db)
