import time

from ..audio.recorder import AudioRecorder

from ..database import Database
from ..tasks import TaskDecisionTree, TaskRecordMessage

from audio.player import AudioPlayer
from tasks import (
    AudioTrack,
    Button,
    TaskAll,
    TaskAny,
    TaskAudioTrack,
    TaskAudioSequence,
    TaskChoice,
    TaskCode,
    TaskLoop,
    TaskSequence,
    TaskWait,
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


class FakeAudioRecorder(AudioRecorder):
    def __init__(self):
        self.is_recording = False
        self.filename = None

    def start(self):
        self.is_recording = True

    def tick(self):
        pass

    def stop(self) -> None:
        self.is_recording = False

    def save(self, filename: str) -> None:
        self.filename = filename

    def reset(self) -> None:
        self.is_recording = False


class MockDatabase(Database):
    def __init__(self, db):
        super().__init__(":memory:")
        super().create_tables()


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
    task.tick()
    assert not task.is_complete()
    time.sleep(0.11)
    task.tick()
    assert not task.is_complete()
    time.sleep(0.11)
    task.tick()
    assert task.is_complete()


def test_task_any():
    task = TaskAny([TaskWait(0.1), TaskWait(0.2), TaskWait(0.3)])
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    time.sleep(0.15)
    task.tick()
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
    assert task.code_string() == "123"


def test_task_audio():
    audio_player = FakeAudioPlayer()
    task = TaskAudioTrack(AudioTrack.INTRO, audio_player)
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    assert audio_player.is_playing
    assert audio_player.filename.endswith(AudioTrack.INTRO.value)
    audio_player.stop()
    assert task.is_complete()


def test_task_audio_sequence():
    audio_player = FakeAudioPlayer()
    task = TaskAudioSequence("123", audio_player)
    assert not task.is_complete()
    task.start()
    assert not task.is_complete()
    assert audio_player.is_playing
    assert audio_player.filename.endswith("/1.wav")
    audio_player.stop()
    task.tick()

    assert not task.is_complete()
    assert audio_player.is_playing
    assert audio_player.filename.endswith("/2.wav")
    audio_player.stop()
    task.tick()

    assert not task.is_complete()
    assert audio_player.is_playing
    assert audio_player.filename.endswith("/3.wav")
    audio_player.stop()
    task.tick()
    assert task.is_complete()


def test_task_loop():
    inner_task = TaskWait(0.1)
    task = TaskLoop(inner_task)
    task.start()
    assert not task.is_complete()
    time.sleep(0.15)
    task.tick()
    assert not task.is_complete()
    time.sleep(0.15)
    task.tick()
    assert not task.is_complete()
    task.stop()
    assert task.is_complete()


def test_task_decision_tree():
    task = TaskDecisionTree(
        {Button.NUM_0.value: TaskWait(0.1), Button.NUM_1.value: TaskWait(0.2)}
    )
    task.start()
    assert not task.is_complete()
    time.sleep(0.15)
    task.tick()
    assert not task.is_complete()
    task.on_button(Button.NUM_0)
    task.tick()
    assert not task.is_complete()
    time.sleep(0.15)
    task.tick()
    assert task.is_complete()


def test_task_record_message():
    audio_recorder = FakeAudioRecorder()
    task = TaskRecordMessage(audio_recorder, DB=MockDatabase)
    task.start()
    assert audio_recorder.is_recording
    task.tick()
    assert not task.is_complete()
    task.on_button(Button.STAR)
    task.tick()
    assert audio_recorder.is_recording is False
    assert audio_recorder.filename is not None
    assert task.is_complete()
