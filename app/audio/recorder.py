import logging
import subprocess
import sys
import os


class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.log = logging.getLogger("Audio.Recorder")
        # Get the ID of the audio hardware device
        self.hw = subprocess.check_output(["./get-audio-hw.sh"], shell=True).decode(
            "utf-8"
        )

    def start(self):
        self.log.debug("Starting a recording session")
        self.is_recording = True
        self._p = subprocess.Popen(
            [
                "afrecord" if sys.platform == "darwin" else "arecord",
                "-D",
                "sysdefault:CARD=" + self.hw,
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
        try:
            os.rename("tmp.wav", filename)
        except FileNotFoundError:
            pass

    def reset(self) -> None:
        self.is_recording = False
