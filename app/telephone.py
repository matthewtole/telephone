from database import Database


class Telephone:
    def __init__(self, database: Database):
        self.database = database

    def test(self):
        self.database.add_recording(100)
        self.database.add_recording(200)
        print(self.database.get_recording_by_id(2))

    def play_recording(self, recording_id):
        print(recording_id)
