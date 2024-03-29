CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP NOT NULl,
  filename TEXT NOT NULL,
  duration INT NOT NULl,
  play_count INT NOT NULl DEFAULT 0,
  last_played_at TIMESTAMP,
  is_deleted INT NOT NULL DEFAULT 0,
  process_state INT NOT NULL DEFAULT 0
)