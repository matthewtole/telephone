import logging
import pyaudio
import wave


class AudioRecorder:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.log = logging.getLogger("Audio.Recorder")

    def start(self):
        self.log.debug('Starting a recording session')
        self.stream = self.audio.open(
            format=AudioRecorder.FORMAT,
            channels=AudioRecorder.CHANNELS,
            rate=AudioRecorder.RATE,
            input=True,
            frames_per_buffer=AudioRecorder.CHUNK)
        self.frames = []
        self.is_recording = True

    def tick(self) -> None:
        if self.is_recording:
            data = self.stream.read(AudioRecorder.CHUNK)
            self.frames.append(data)

    def stop(self) -> None:
        self.log.debug('Ending a recording session')
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def save(self, filename: str) -> None:
        self.log.debug('Saving a recording session')
        wf = wave.open(filename, 'wb')
        wf.setnchannels(AudioRecorder.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(AudioRecorder.FORMAT))
        wf.setframerate(AudioRecorder.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.frames = []
