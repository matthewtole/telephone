import argparse
import time
from input import PhoneInput
from input import KeyboardInput
from database import Database
from telephone import Telephone
import logging
import os

LOG_FILE = 'telephone.log'
DB_FILE = 'telephone.db'


def setup():
    logging.basicConfig(
        level=logging.DEBUG,
        filename=LOG_FILE,
        encoding='utf-8',
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    )

    try:
        os.mkdir("temp")
    except FileExistsError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    args = parser.parse_args()

    setup()

    db = Database(DB_FILE)
    db.create_tables()

    if args.input == "phone":
        input = PhoneInput()
    else:
        input = KeyboardInput()

    telephone = Telephone(db, input)
    while True:
        telephone.tick()
        time.sleep(0.1)
