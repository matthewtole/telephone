import logging
import subprocess
import sys
import os


class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.log = logging.getLogger("Audio.Recorder")

    def start(self):
        self.log.debug("Starting a recording session")
        self.is_recording = True
        self._p = subprocess.Popen(
            [
                "afrecord" if sys.platform == "darwin" else "arecord",
                "-D",
                "sysdefault:CARD=2",
                "-d",
                "10",
                "-f",
                "cd",
                "-t",
                "wav",
                "tmp.wav",
            ]
        )

    def tick(self) -> None:
        self.is_recording = self._p.poll() is None

    def stop(self) -> None:
        self.log.debug("Ending a recording session")
        self.is_recording = False
        self._p.kill()

    def save(self, filename: str) -> None:
        self.log.debug("Saving a recording session")
        os.rename("tmp.wav", filename)

    def reset(self) -> None:
        self.is_recording = False
