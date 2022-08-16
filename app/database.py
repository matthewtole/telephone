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


class TableRecording:
    def __init__(self, connection: sqlite3.Connection, log: logging.Logger):
        self.connection = connection
        self.cursor = connection.cursor()
        self.log = log

    def drop(self):
        self.cursor.execute("DROP TABLE recordings")

    def create(self):
        self.log.info("Creating table 'recordings'")
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

    def insert(self, duration: int) -> int:
        self.cursor.execute(
            "INSERT INTO recordings (created_at, duration) VALUES (?, ?)",
            (datetime.datetime.now(), duration),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get(self, id: int) -> Recording:
        result = self.cursor.execute(
            "SELECT * FROM recordings WHERE id=%d" % id
        ).fetchone()
        return Recording(*result)

    def list_with_play_count(self, count: int) -> List[Recording]:
        result = self.cursor.execute(
            "SELECT * FROM recordings WHERE play_count=%d" % count
        ).fetchall()
        return list(map(lambda r: Recording(*r), result))

    def list_unplayed(self) -> List[Recording]:
        return self.list_with_play_count(0)

    def play(self, id: int) -> None:
        self.cursor.execute(
            "UPDATE recordings SET play_count=play_count+1 WHERE id=%d" % id
        )
        self.connection.commit()


class Database:
    def __init__(self, db: str):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.log = logging.getLogger("Database")
        self.recording = TableRecording(self.connection, self.log)

    def create_tables(self):
        self.log.info("Dropping all existing tables")
        try:
            self.recording.drop()
        except sqlite3.OperationalError:
            pass

        self.recording.create()
