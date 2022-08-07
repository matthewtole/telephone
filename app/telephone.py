from database import Database


class Telephone:
    def __init__(self, db: Database):
        self.db = db

    def test(self):
        self.db.add_recording(100)
        self.db.add_recording(200)
        print(self.db.get_recording_by_id(2))
