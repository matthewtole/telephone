import logging
import sqlite3
import datetime
from typing import List, NamedTuple, Optional


class Recording(NamedTuple):
    id: int
    created_at: sqlite3.Timestamp
    duration: int
    play_count: int
    last_played_at: Optional[sqlite3.Timestamp]


class Database:
    def __init__(self, db: str):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.log = logging.getLogger("Database")

    def create_tables(self):
        self.cursor.execute("DROP TABLE recordings")

        self.cursor.execute(
            """
      CREATE TABLE recordings (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at      TIMESTAMP NOT NULl,
        duration        INT NOT NULl,
        play_count      INT NOT NULl DEFAULT 0,
        last_played_at  TIMESTAMP
      )
"""
        )

    def add_recording(self, duration: int) -> int:
        self.cursor.execute(
            "INSERT INTO recordings (created_at, duration) VALUES (?, ?)",
            (datetime.datetime.now(), duration),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get_recording_by_id(self, id: int) -> Recording:
        result = self.cursor.execute(
            "SELECT * FROM recordings WHERE id=%d" % id
        ).fetchone()
        return Recording(*result)

    def get_unplayed_recordings(self) -> List[Recording]:
        return self.get_recordings_with_play_count(0)

    def get_recordings_with_play_count(self, count) -> List[Recording]:
        result = self.cursor.execute(
            "SELECT * FROM recordings WHERE play_count=%d" % count).fetchall()
        return list(map(lambda r: Recording(*r), result))

    def play_recording(self, id: int) -> None:
        self.cursor.execute(
            "UPDATE recordings SET play_count=play_count+1 WHERE id=%d" % id)
        self.connection.commit()
