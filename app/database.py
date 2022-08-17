import logging
import sqlite3
import datetime
from typing import List, NamedTuple, Optional


class Message(NamedTuple):
    id: int
    created_at: sqlite3.Timestamp
    filename: str
    duration: int
    play_count: int
    last_played_at: Optional[sqlite3.Timestamp]


class TableMessages:
    TABLE_NAME = "messages"

    def __init__(self, connection: sqlite3.Connection, log: logging.Logger):
        self.connection = connection
        self.cursor = connection.cursor()
        self.log = log

    def drop(self):
        self.cursor.execute("DROP TABLE %s" % TableMessages.TABLE_NAME)

    def create(self):
        self.log.info("Creating table '%s'" % TableMessages.TABLE_NAME)
        self.cursor.execute(
            """
      CREATE TABLE %s (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at      TIMESTAMP NOT NULl,
        filename        TEXT NOT NULL,
        duration        INT NOT NULl,
        play_count      INT NOT NULl DEFAULT 0,
        last_played_at  TIMESTAMP
      )
"""
            % TableMessages.TABLE_NAME
        )

    def insert(self, filename: str, duration: int) -> int:
        self.cursor.execute(
            "INSERT INTO %s (created_at, filename, duration) VALUES (?, ?, ?)"
            % TableMessages.TABLE_NAME,
            (datetime.datetime.now(), filename, duration),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get(self, id: int) -> Message:
        result = self.cursor.execute(
            "SELECT * FROM %s WHERE id=%d" % (TableMessages.TABLE_NAME, id)
        ).fetchone()
        return Message(*result)

    def list_with_play_count(self, count: int) -> List[Message]:
        result = self.cursor.execute(
            "SELECT * FROM %s WHERE play_count=%d" % (TableMessages.TABLE_NAME, count)
        ).fetchall()
        return list(map(lambda r: Message(*r), result))

    def list_unplayed(self) -> List[Message]:
        return self.list_with_play_count(0)

    def play(self, id: int) -> None:
        self.cursor.execute(
            "UPDATE %s SET play_count=play_count+1 WHERE id=%d"
            % (TableMessages.TABLE_NAME, id)
        )
        self.connection.commit()

    def count(self) -> int:
        result = self.cursor.execute(
            "SELECT COUNT(*) as count FROM %s" % TableMessages.TABLE_NAME
        ).fetchone()
        return result[0]


class Database:
    def __init__(self, db: str):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.log = logging.getLogger("Database")
        self.messages = TableMessages(self.connection, self.log)

    def create_tables(self):
        self.log.info("Dropping all existing tables")
        try:
            self.messages.drop()
        except sqlite3.OperationalError:
            pass

        self.messages.create()
