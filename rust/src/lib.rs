pub mod models;
pub mod schema;

use chrono::Local;
use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;

use self::models::NewMessage;

pub fn create_message(connection: &mut SqliteConnection, filename: &str, duration: &i32) {
    use crate::schema::messages;

    let new_message = NewMessage { filename, duration };

    diesel::insert_into(messages::table)
        .values(&new_message)
        .execute(connection)
        .expect("Error saving new post");
}

pub fn add_message_listen(conn: &mut SqliteConnection, message_id: &i32) {
    use self::schema::messages::dsl::*;

    diesel::update(messages.filter(id.eq(message_id)))
        .set((
            play_count.eq(play_count + 1),
            last_played_at.eq(Local::now().naive_local()),
        ))
        .execute(conn)
        .expect("Failed to update message");
}
