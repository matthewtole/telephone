use crate::schema::messages;
use diesel::prelude::*;

#[derive(Queryable, Debug)]
pub struct Message {
    pub id: i32,
    pub created_at: chrono::NaiveDateTime,
    pub filename: String,
    pub duration: i32,
    pub play_count: i32,
    pub last_played_at: Option<chrono::NaiveDateTime>,
}

#[derive(Insertable)]
#[diesel(table_name = messages)]
pub struct NewMessage<'a> {
    pub filename: &'a str,
    pub duration: &'a i32,
}
