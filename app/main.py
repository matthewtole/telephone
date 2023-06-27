import time
import click
import logging
import os
from threading import Thread
from audio.recorder import AudioRecorder
from audio_track import AudioTrack
from audio.player import AudioPlayer
from input_manager import CircuitBoard, InputManager
from telephone import Telephone
import tasks
import shutil
from database import Database
from scripts.clean import clean_messages

from config import DATABASE_FILE, LOG_FILE, TEMP_DIR, MESSAGES_DIR


def setup_dirs():
    logging.basicConfig(
        level=logging.DEBUG,
        filename=LOG_FILE,
        encoding="utf-8",
        format="%(asctime)s|%(levelname)s|%(name)s|%(message)s",
    )

    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        os.mkdir(TEMP_DIR)
    except FileExistsError:
        pass

    try:
        os.mkdir(MESSAGES_DIR)
    except FileExistsError:
        pass


@click.group()
def telephone():
    pass


@telephone.command()
def setup():
    setup_dirs()
    db: Database = Database(DATABASE_FILE)
    db.create_tables()
    db.connection.close()


@telephone.command()
def clean():
    clean_messages()


@telephone.command()
def audio():
    audio_player = AudioPlayer()
    audio_player.play("audio/intro-01.wav")
    while audio_player.is_playing:
        audio_player.tick()
        time.sleep(0.1)


@telephone.command()
def record():
    audio_recorder = AudioRecorder()
    audio_recorder.start()
    start_time = time.time()
    while time.time() < start_time + 10:
        audio_recorder.tick()
        time.sleep(0.05)
    audio_recorder.tick()
    audio_recorder.save("demo.wav")


class ButtonLogger:
    def __init__(self, input: InputManager):
        self.input = input

    def run(self):
        while True:
            button = self.input.button_pressed()
            if button is not None:
                print(button)
            time.sleep(0.05)


@telephone.command()
def buttons():
    input_manager = CircuitBoard()
    logger = ButtonLogger(input_manager)
    logger = Thread(target=logger.run)
    logger.start()
    input_manager.start()


def root_task():
    return tasks.TaskSequence(
        [
            tasks.TaskAudioTrack(AudioTrack.INTRO),
            tasks.TaskLoop(
                tasks.TaskSequence(
                    [
                        tasks.TaskAudioTrack(AudioTrack.MENU_1),
                        tasks.TaskDecisionTree(
                            {
                                1: tasks.TaskSequence(
                                    [
                                        tasks.TaskAudioTrack(AudioTrack.RECORD_INTRO),
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.BEEP),
                                        tasks.TaskRecordMessage(),
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.RECORD_OUTRO),
                                    ]
                                ),
                                2: tasks.TaskPlayMessage(),
                            }
                        ),
                        tasks.TaskWait(1),
                    ]
                )
            ),
        ]
    )


@click.option("-i", "--input", is_flag=False)
@telephone.command()
def start(input: str):
    input_manager = CircuitBoard()
    phone = Telephone(input_manager, root_task)

    phone_thread = Thread(target=phone.start)
    phone_thread.start()
    input_manager.start()


if __name__ == "__main__":
    telephone(prog_name="telephone")
