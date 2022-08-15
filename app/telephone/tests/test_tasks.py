import time
from ..tasks import (
    Button,
    TaskAll,
    TaskAny,
    TaskChoice,
    TaskCode,
    TaskSequence,
    TaskWait
)


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
