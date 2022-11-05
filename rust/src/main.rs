use database::establish_connection;
use diesel::SqliteConnection;
use log::info;
use simple_logger::SimpleLogger;
use std::thread;
mod action;
mod database;
mod messages;
mod models;
mod schema;
use std::collections::VecDeque;
use std::time::Duration;

fn boot_checks(connection: &mut SqliteConnection) {
    info!("Running boot up checks.");
    assert!(
        messages::count(connection) >= 0,
        "Failed to access to the messages table."
    );
    info!("All boot up checks completed successfully!");
}

fn main() {
    SimpleLogger::new().init().unwrap();

    let mut connection = establish_connection();
    boot_checks(&mut connection);

    let mut actions: VecDeque<action::Action> = VecDeque::new();
    actions.push_back(action::Action::WaitForAll(vec![
        action::Action::Wait(Duration::from_secs(2)),
        action::Action::PlayAudio(String::from("../audio/beep.wav")),
    ]));

    while actions.len() > 0 {
        let action = actions.pop_front();
        match action {
            Some(action) => {
                let handle = thread::spawn(|| action::execute_action(action));
                while !handle.is_finished() {
                    thread::sleep(std::time::Duration::from_millis(10));
                }
            }
            None => {}
        }
    }
}
