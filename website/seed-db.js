const sqlite3 = require('sqlite3');
const { open } = require('sqlite');
const { DateTime } = require('luxon');
const fs = require('fs/promises');

async function createMessagesTable(db) {
  db.exec('DROP TABLE messages');
  db.exec((await fs.readFile('../sql/messages.sql')).toString());
}

async function createPlaysTable(db) {
  db.exec('DROP TABLE plays');
  db.exec((await fs.readFile('../sql/plays.sql')).toString());
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
  await createPlaysTable(db);
  await seedMessages(db);
}

seed().then(console.log).catch(console.error);
