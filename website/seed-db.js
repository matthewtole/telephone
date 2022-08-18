const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const { DateTime } = require('luxon');

async function createMessagesTable(db) {
  db.exec('DROP TABLE messages');
  db.exec(`CREATE TABLE messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TIMESTAMP NOT NULl,
    filename        TEXT NOT NULL,
    duration        INT NOT NULl,
    play_count      INT NOT NULl DEFAULT 0,
    last_played_at  TIMESTAMP
  )
  `);
}

async function seedMessages(db) {
  for (const index in new Array(10).fill(null)) {
    await db.exec(
      `INSERT INTO messages 
        (created_at, filename, duration, play_count) VALUES 
        ("${DateTime.now().toSQL()}", "${index}.wav", ${Math.floor(
        Math.random() * 100
      )}, ${Math.floor(Math.random() * 20)})`
    );
  }
}

async function seed() {
  const db = await open({
    filename: '../telephone.db',
    driver: sqlite3.Database,
  });
  await createMessagesTable(db);
  await seedMessages(db);
}

seed().then(console.log).catch(console.error);
