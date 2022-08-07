import sqlite3
import datetime
from typing import Any


class Database:
    def __init__(self, db: str):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        try:
            self.cursor.execute("DROP TABLE recordings")
        except:
            pass

        self.cursor.execute('''
      CREATE TABLE recordings (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at      TIMESTAMP NOT NULl, 
        duration        INT NOT NULl,
        play_count      INT NOT NULl DEFAULT 0,
        last_played_at  TIMESTAMP
      )
''')

    def add_recording(self, duration: int) -> int:
        self.cursor.execute(
            "INSERT INTO recordings (created_at, duration) VALUES (?, ?)", (datetime.datetime.now(), duration))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_recording_by_id(self, id: int) -> Any:
        return self.cursor.execute("SELECT * FROM recordings WHERE id=%d" % id).fetchone()
