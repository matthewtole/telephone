import time
import click
import logging
import os
from threading import Thread
from audio.process import AudioProcessor
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


class HandsetLogger:
    def __init__(self, input: InputManager):
        self.input = input

    def run(self):
        while True:
            print(self.input.is_handset_up())
            time.sleep(1)


@telephone.command()
def buttons():
    input_manager = CircuitBoard()
    logger = ButtonLogger(input_manager)
    logger = Thread(target=logger.run)
    logger.start()
    input_manager.start()


@telephone.command()
def handset():
    input_manager = CircuitBoard()
    logger = HandsetLogger(input_manager)
    logger = Thread(target=logger.run)
    logger.start()
    input_manager.start()


def processor():
    db: Database = Database(DATABASE_FILE)
    processor = AudioProcessor(db)
    processor.start()


@telephone.command()
def process():
    thread = Thread(target=processor)
    thread.start()


def root_task():
    return tasks.TaskSequence(
        [
            tasks.TaskWait(1),
            tasks.TaskAudioTrack(AudioTrack.INTRO),
            tasks.TaskLoop(
                tasks.TaskSequence(
                    [
                        tasks.TaskDecisionTree(
                            {
                                1: tasks.TaskSequence(
                                    [
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.RECORD_INTRO),
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.BEEP),
                                        tasks.TaskRecordMessage(),
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.RECORD_OUTRO),
                                    ]
                                ),
                                2: tasks.TaskSequence(
                                    [
                                        tasks.TaskWait(0.5),
                                        tasks.TaskAudioTrack(AudioTrack.LISTEN_INTRO),
                                        tasks.TaskWait(0.25),
                                        tasks.TaskPlayMessage(),
                                        tasks.TaskWait(0.25),
                                        tasks.TaskAudioTrack(AudioTrack.LISTEN_OUTRO),
                                        tasks.TaskWait(0.5),
                                    ]
                                ),
                                3: tasks.TaskAudioTrack(AudioTrack.INVALID_OPTION_1),
                                4: tasks.TaskAudioTrack(AudioTrack.INVALID_OPTION_2),
                                5: tasks.TaskAudioTrack(AudioTrack.INVALID_OPTION_3),
                                6: tasks.TaskAudioTrack(AudioTrack.INVALID_OPTION_4),
                                7: tasks.TaskAudioTrack(AudioTrack.INVALID_OPTION_5),
                                8: tasks.TaskAudioTrack(AudioTrack.INVALID_OPTION_6),
                                0: tasks.TaskLoop(
                                    tasks.TaskSequence(
                                        [
                                            tasks.TaskWait(0.5),
                                            tasks.TaskAudioTrack(
                                                AudioTrack.HOLD_MESSAGE
                                            ),
                                            tasks.TaskWait(0.5),
                                            tasks.TaskAudioTrack(AudioTrack.HOLD_MUSIC),
                                        ]
                                    )
                                ),
                            },
                            invalid_choice=tasks.TaskAudioTrack(
                                AudioTrack.INVALID_OPTION_3
                            ),
                            intro_task=tasks.TaskAudioTrack(AudioTrack.MENU_1),
                            timeout=10,
                        ),
                        tasks.TaskWait(1),
                    ]
                )
            ),
        ]
    )


@telephone.command()
def start():
    setup_dirs()

    input_manager = CircuitBoard()
    phone = Telephone(input_manager, root_task)

    process_thread = Thread(target=processor)
    process_thread.start()

    phone_thread = Thread(target=phone.start)
    phone_thread.start()
    input_manager.start()


if __name__ == "__main__":
    telephone(prog_name="telephone")
