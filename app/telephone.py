class Telephone:
  def __init__(self, db):
    self.db = db

  def test(self):
    self.db.add_recording(100)