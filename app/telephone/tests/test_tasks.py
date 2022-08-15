import time

from ...audio.player import AudioPlayer
from ..tasks import (
    AudioTrack,
    Button,
    TaskAll,
    TaskAny,
    TaskAudio,
    TaskChoice,
    TaskCode,
    TaskSequence,
    TaskWait
)


class FakeAudioPlayer(AudioPlayer):
    def __init__(self):
        self.is_playing = False

    def play(self, filename: str) -> None:
        self.filename = filename
        self.is_playing = True

    def stop(self) -> None:
        self.is_playing = False

    def tick(self) -> None:
        pass


def test_task_wait():
    task = TaskWait(0.5)
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    time.sleep(0.25)
    assert not task.is_complete()
    time.sleep(0.25)
    assert task.is_complete()


def test_task_all():
    task = TaskAll([TaskWait(0.1), TaskWait(0.2), TaskWait(0.3)])
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    time.sleep(0.11)
    assert not task.is_complete()
    time.sleep(0.11)
    assert not task.is_complete()
    time.sleep(0.11)
    assert task.is_complete()


def test_task_any():
    task = TaskAny([TaskWait(0.1), TaskWait(0.2), TaskWait(0.3)])
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    time.sleep(0.15)
    assert task.is_complete()


def test_task_sequence():
    task = TaskSequence([TaskWait(0.2), TaskWait(0.2), TaskWait(0.2)])
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    time.sleep(0.25)
    assert not task.is_complete()
    time.sleep(0.2)
    assert not task.is_complete()
    time.sleep(0.2)
    assert task.is_complete()


def test_task_choice():
    task = TaskChoice()
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    task.on_button(Button.NUM_0)
    assert task.is_complete()
    assert task.choice == Button.NUM_0.value


def test_task_code():
    task = TaskCode()
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    task.on_button(Button.NUM_1)
    assert not task.is_complete()
    task.on_button(Button.NUM_2)
    assert not task.is_complete()
    task.on_button(Button.NUM_3)
    assert not task.is_complete()
    task.on_button(Button.STAR)
    assert not task.is_complete()
    task.on_button(Button.POUND)
    assert task.is_complete()
    assert task.code_string() == '123'


def test_task_audio():
    audio_player = FakeAudioPlayer()
    task = TaskAudio(AudioTrack.INTRO, audio_player)
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    assert audio_player.is_playing
    assert audio_player.filename.endswith(AudioTrack.INTRO.value)
    audio_player.stop()
    assert task.is_complete()
