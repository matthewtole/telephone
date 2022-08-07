from database import Database


def test_add_recording():
    db = Database(":memory:")
    db.create_tables()
    db.add_recording(100)
    recording = db.get_recording_by_id(1)
    assert recording.id == 1
    assert recording.duration == 100
    assert recording.last_played_at == None
    assert recording.play_count == 0


def test_unplayed_recordings():
    db = Database(":memory:")
    db.create_tables()
    db.add_recording(100)
    db.add_recording(200)
    db.add_recording(300)

    assert len(db.get_unplayed_recordings()) == 3

    db.play_recording(1)
    db.play_recording(3)

    assert len(db.get_unplayed_recordings()) == 1

    db.play_recording(1)
    db.play_recording(2)

    assert len(db.get_unplayed_recordings()) == 0

    assert(len(db.get_recordings_with_play_count(1))) == 2
    assert(len(db.get_recordings_with_play_count(2))) == 1
