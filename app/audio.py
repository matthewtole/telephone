import logging
import time
import pyaudio
import wave
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class AudioRecording:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.log = logging.getLogger("AudioRecording")

    def start_recording(self):
        self.log.debug('[audio] Starting a recording session')
        self.stream = self.audio.open(format=FORMAT,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK)
        self.frames = []
        self.is_recording = True

    def tick(self):
        if self.is_recording:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

    def stop_recording(self):
        self.log.debug('[audio] Ending a recording session')
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def save_recording(self, filename: str):
        self.log.debug('[audio] Saving a recording session')
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.frames = []


class AudioPlayer:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_playing = False

    def callback(self, in_data, frame_count, time_info, status):
        data = self.wave_file.readframes(frame_count)
        return (data, pyaudio.paContinue)

    def play(self, filename):

        self.wave_file = wave.open(filename, 'rb')
        self.stream = self.audio.open(format=self.audio.get_format_from_width(self.wave_file.getsampwidth()),
                                      channels=self.wave_file.getnchannels(),
                                      rate=self.wave_file.getframerate(),
                                      output=True,
                                      stream_callback=self.callback)

        self.stream.start_stream()
        self.is_playing = True

    def tick(self):
        if not self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            self.wave_file.close()
            self.is_playing = False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        filename='telephone.log',
                        encoding='utf-8',
                        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")

    try:
        os.mkdir("temp")
    except FileExistsError:
        pass
    recording = AudioRecording()
    start = time.time()
    recording.start_recording()
    while (time.time() - start) <= 3:
        recording.tick()
    recording.stop_recording()
    recording.save_recording("temp/test.wav")
    print("Recording saved")

    # player = AudioPlayer()
    # player.play("temp/test.wav")
    # while player.is_playing:
    #     player.tick()
    #     time.sleep(0.1)
