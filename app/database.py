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
    is_deleted: int
    process_state: int


class Play(NamedTuple):
    id: int
    message_id: int
    played_at: sqlite3.Timestamp
    play_duration: int


class TableMessages:
    """
    Database table for managing the recorded messages.
    """

    TABLE_NAME = "messages"

    def __init__(self, connection: sqlite3.Connection, log: logging.Logger):
        self.connection = connection
        self.cursor = connection.cursor()
        self.log = log

    def drop(self):
        self.cursor.execute("DROP TABLE %s" % TableMessages.TABLE_NAME)

    def create(self):
        self.log.info("Creating table '%s'" % TableMessages.TABLE_NAME)
        sql = "".join(open("sql/messages.sql", "r").readlines())
        self.cursor.execute(sql)

    def insert(self, filename: str, duration: int) -> Optional[int]:
        self.cursor.execute(
            "INSERT INTO %s (created_at, filename, duration) VALUES (?, ?, ?)"
            % TableMessages.TABLE_NAME,
            (datetime.datetime.now(), filename, duration),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get(self, id: int) -> Message:
        """
        Get a single message given the ID
        """
        result = self.cursor.execute(
            "SELECT * FROM %s WHERE id=%d" % (TableMessages.TABLE_NAME, id)
        ).fetchone()
        return Message(*result)

    def get_by_filename(self, filename: str) -> Optional[Message]:
        result = self.cursor.execute(
            "SELECT * FROM messages WHERE filename='%s'" % filename
        ).fetchone()
        return Message(*result) if result is not None else None

    def list_playback_suggestions(self, count: int) -> List[Message]:
        """
        Get all of the messages with the given number of play counts.
        """
        one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        ten_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=10)
        result = self.cursor.execute(
            """
            SELECT *
            FROM %s
            WHERE play_count=%d
                AND is_deleted=0
                AND process_state=1
                AND created_at < "%s"
                AND last_played_at < "%s"
            ORDER BY filename
            LIMIT 50
            """
            % (
                TableMessages.TABLE_NAME,
                count,
                one_hour_ago.strftime("%Y-%m-%d %H:%M:%S"),
                ten_minutes_ago.strftime("%Y-%m-%d %H:%M:%S"),
            )
        ).fetchall()
        return list(map(lambda r: Message(*r), result))

    def list_with_play_count(self, count: int) -> List[Message]:
        """
        Get all of the messages with the given number of play counts.
        """
        result = self.cursor.execute(
            "SELECT * FROM %s WHERE play_count=%d AND is_deleted=0 AND process_state=1"
            % (TableMessages.TABLE_NAME, count)
        ).fetchall()
        return list(map(lambda r: Message(*r), result))

    def list_unplayed(self) -> List[Message]:
        """
        Get all of the messages that haven't been played yet.
        """
        return self.list_with_play_count(0)

    def play(self, id: int) -> None:
        """
        Mark a message as being played.
        Increases the play count by 1 and sets the last played at timestamp to the current time
        """
        self.cursor.execute(
            "UPDATE %s SET play_count=play_count+1, last_played_at=? WHERE id=?"
            % (TableMessages.TABLE_NAME),
            (datetime.datetime.now(), id),
        )
        self.connection.commit()

    def count(self) -> int:
        """
        Return the total count of messages
        """
        result = self.cursor.execute(
            "SELECT COUNT(*) as count FROM %s WHERE is_deleted=0 AND process_state=1"
            % TableMessages.TABLE_NAME
        ).fetchone()
        return result[0]

    def get_unprocessed(self) -> Optional[Message]:
        """
        Get a message that hasn't been processed yet
        """
        result = self.cursor.execute(
            "SELECT * FROM %s WHERE process_state=0 LIMIT 1" % TableMessages.TABLE_NAME
        ).fetchone()
        return Message(*result) if result is not None else None

    def mark_processed(self, id: int) -> None:
        self.cursor.execute(
            "UPDATE %s SET process_state=1 WHERE id=%d"
            % (TableMessages.TABLE_NAME, id),
        )
        self.connection.commit()


class TablePlays:
    """
    Database table for managing the recorded messages.
    """

    TABLE_NAME = "plays"

    def __init__(self, connection: sqlite3.Connection, log: logging.Logger):
        self.connection = connection
        self.cursor = connection.cursor()
        self.log = log

    def drop(self):
        self.cursor.execute("DROP TABLE %s" % TablePlays.TABLE_NAME)

    def create(self):
        self.log.info("Creating table '%s'" % TablePlays.TABLE_NAME)
        sql = "".join(open("sql/%s.sql" % TablePlays.TABLE_NAME, "r").readlines())
        self.cursor.execute(sql)

    def insert(self, message_id: int) -> Optional[int]:
        self.cursor.execute(
            "INSERT INTO %s (message_id, played_at) VALUES (?, ?)"
            % TablePlays.TABLE_NAME,
            (message_id, datetime.datetime.now()),
        )
        self.connection.commit()
        return self.cursor.lastrowid


class Database:
    def __init__(self, db: str):
        self.connection = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.connection.cursor()
        self.log = logging.getLogger("Database")
        self.messages = TableMessages(self.connection, self.log)
        self.plays = TablePlays(self.connection, self.log)

    def create_tables(self):
        self.log.info("Dropping all existing tables")
        try:
            self.messages.drop()
            self.plays.drop()
        except sqlite3.OperationalError:
            pass

        self.messages.create()
        self.plays.create()
