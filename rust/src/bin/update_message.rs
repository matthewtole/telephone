use rust::*;

fn main() {
    let id: i32 = 1;
    let connection = &mut establish_connection();
    add_message_listen(connection, &id);
}
