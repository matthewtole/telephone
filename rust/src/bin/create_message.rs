use rust::*;
use std::io::{stdin, Read};

fn main() {
    let connection = &mut establish_connection();

    let mut filename = String::new();
    let duration = 0;

    println!("What would you like your filename to be?");
    stdin().read_line(&mut filename).unwrap();

    create_message(connection, &filename, &duration);
}

#[cfg(not(windows))]
const EOF: &str = "CTRL+D";

#[cfg(windows)]
const EOF: &str = "CTRL+Z";
