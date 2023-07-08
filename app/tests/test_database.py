from ..database import Database


def test_add_message():
    db = Database(":memory:")
    db.create_tables()
    db.messages.insert("test.wav", 100)
    message = db.messages.get(1)
    assert message.id == 1
    assert message.filename == "test.wav"
    assert message.duration == 100
    assert message.last_played_at == None  # noqa: E711
    assert message.play_count == 0


def test_count():
    db = Database(":memory:")
    db.create_tables()

    assert db.messages.count() == 0

    db.messages.insert("test-1.wav", 100)
    db.messages.insert("test-2.wav", 200)
    assert db.messages.count() == 2
