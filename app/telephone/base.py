import time
from audio.player import AudioPlayer
from database import Database


class Button:
    pass


class Task:
    pass


class AudioTask(Task):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self.audio_player = AudioPlayer()
        self.audio_player.play(filename)

    def is_complete(self) -> bool:
        return self.audio_player.is_playing

    def abort(self) -> None:
        return self.audio_player.stop()


class Telephone:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.current_task = None

    def start(self):
        self.current_task = AudioTask("audio/intro-01.wav")
        while not self.current_task.is_complete():
            time.sleep(0.1)

    def on_button(self, button: Button) -> None:
        pass
