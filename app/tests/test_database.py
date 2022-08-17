from ..database import Database


def test_add_message():
    db = Database(":memory:")
    db.create_tables()
    db.messages.insert(100)
    message = db.messages.get(1)
    assert message.id == 1
    assert message.duration == 100
    assert message.last_played_at == None  # noqa: E711
    assert message.play_count == 0


def test_unplayed_messages():
    db = Database(":memory:")
    db.create_tables()
    db.messages.insert(100)
    db.messages.insert(200)
    db.messages.insert(300)

    assert len(db.messages.list_unplayed()) == 3

    db.messages.play(1)
    db.messages.play(3)

    assert len(db.messages.list_unplayed()) == 1

    db.messages.play(1)
    db.messages.play(2)

    assert len(db.messages.list_unplayed()) == 0

    assert len(db.messages.list_with_play_count(1)) == 2
    assert len(db.messages.list_with_play_count(2)) == 1
