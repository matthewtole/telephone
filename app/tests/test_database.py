from ..database import Database


def test_add_recording():
    db = Database(":memory:")
    db.create_tables()
    db.recording.insert(100)
    recording = db.recording.get(1)
    assert recording.id == 1
    assert recording.duration == 100
    assert recording.last_played_at == None  # noqa: E711
    assert recording.play_count == 0


def test_unplayed_recordings():
    db = Database(":memory:")
    db.create_tables()
    db.recording.insert(100)
    db.recording.insert(200)
    db.recording.insert(300)

    assert len(db.recording.list_unplayed()) == 3

    db.recording.play(1)
    db.recording.play(3)

    assert len(db.recording.list_unplayed()) == 1

    db.recording.play(1)
    db.recording.play(2)

    assert len(db.recording.list_unplayed()) == 0

    assert len(db.recording.list_with_play_count(1)) == 2
    assert len(db.recording.list_with_play_count(2)) == 1
