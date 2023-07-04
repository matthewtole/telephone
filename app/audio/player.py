import logging
import sys
import subprocess


class AudioPlayer:
    def __init__(self):
        super().__init__()
        self.is_playing = False
        self.log = logging.getLogger("Audio.Player")
        self._p = None

    def play(self, filename: str) -> None:
        self.log.log(logging.INFO, "Playing %s" % filename)
        self.is_playing = True
        self._p = subprocess.Popen(
            ["afplay" if sys.platform == "darwin" else "aplay", filename]
        )

    def stop(self) -> None:
        self.log.error("Stopping audio playback")
        self._p.terminate() if self._p is not None else None
        self._p.kill() if self._p is not None else None
        self.log.log(logging.INFO, "Audio playback stopped")

    def tick(self) -> None:
        self.is_playing = self._p.poll() is None if self._p is not None else False
