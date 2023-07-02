import logging
import subprocess
from os.path import join
import os
import time
from config import MESSAGES_DIR
from database import Database, Message


class AudioProcessor:
    def __init__(self, db: Database) -> None:
        self.log = logging.getLogger("Audio.Processor")
        self.db = db

    def start(self) -> None:
        while True:
            message = self.db.messages.get_unprocessed()
            if message is None:
                time.sleep(1)
                continue

            self.process(message)
            os.rename("processed.wav", join(MESSAGES_DIR, message.filename))
            self.db.messages.mark_processed(message.id)

    def process(self, message: Message) -> None:
        self.log.info("Processing message %d" % message.id)
        handle = subprocess.Popen(
            [
                "ffmpeg",
                "-i",
                join(MESSAGES_DIR, message.filename),
                "-y",
                # "-loglevel",
                # "quiet",
                "-filter:a",
                "loudnorm",
                "processed.wav",
            ]
        )
        while True:
            if handle.poll() is not None:
                break
            time.sleep(0.1)
