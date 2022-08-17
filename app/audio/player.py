import logging
from typing import Mapping, Optional
import pyaudio
import wave


class AudioPlayer:
    def __init__(self):
        super().__init__()
        self.audio = pyaudio.PyAudio()
        self.is_playing = False
        self.log = logging.getLogger("Audio.Player")
        self.stream = None

    def callback(
        self,
        in_data: Optional[bytes],
        frame_count: int,
        time_info: Mapping[str, float],
        status: int,
    ):
        data = self.wave_file.readframes(frame_count)
        return (data, pyaudio.paContinue)

    def play(self, filename: str) -> None:
        self.log.log(logging.INFO, "Playing %s" % filename)
        self.wave_file = wave.open(filename, "rb")
        self.stream = self.audio.open(
            format=self.audio.get_format_from_width(self.wave_file.getsampwidth()),
            channels=self.wave_file.getnchannels(),
            rate=self.wave_file.getframerate(),
            output=True,
            stream_callback=self.callback,
        )

        self.stream.start_stream()
        self.is_playing = True

    def stop(self) -> None:
        self.log.log(logging.INFO, "Audio playback stopped")
        if self.stream is not None:
            self.stream.stop_stream()

    def tick(self) -> None:
        if self.is_playing and self.stream is not None and not self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            self.wave_file.close()
            self.is_playing = False
