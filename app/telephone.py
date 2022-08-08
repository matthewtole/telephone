import logging
from audio import AudioPlayer
from input import Input
from database import Database


class Telephone:
    def __init__(self, database: Database, input: Input):
        self.log = logging.getLogger("Telephone")
        self.database = database
        self.input = input
        self.audio_player = AudioPlayer()
        self.log.info("Audio started")
        self.audio_player.play("app/audio/intro-01.wav")
        self.log.info("Audio completed")

    def tick(self):
        button = self.input.button_pressed()
        if button is None:
            pass
        else:
            print("Button: %s" % button)
