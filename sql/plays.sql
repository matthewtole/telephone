CREATE TABLE plays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id INTEGER NOT NULL REFERENCES messages(id),
  played_at TIMESTAMP NOT NULl,
  play_duration INTEGER
)