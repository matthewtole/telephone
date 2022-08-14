import time
from ..tasks import TaskAll, TaskAny, TaskWait


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
