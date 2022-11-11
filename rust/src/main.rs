use database::establish_connection;
use diesel::SqliteConnection;
use log::{error, info};
use simple_logger::SimpleLogger;
use std::process::exit;
use std::thread;
use strum::IntoEnumIterator;
mod action;
mod database;
mod messages;
mod models;
mod schema;
use std::collections::VecDeque;
use std::time::Duration;

mod audio;

use crate::audio::audio::Track;

fn boot_checks(connection: &mut SqliteConnection) -> Result<(), &str> {
    info!("Running boot up checks.");
    if messages::count(connection) < 0 {
        return Err("Missing database table: messages");
    }

    for audio in Track::iter() {
        if !std::path::Path::new(&audio.path()).exists() {
            return Err("Missing audio file");
        }
    }

    for i in 1..9 {
        if !std::path::Path::new(&audio::audio::digit_path(i)).exists() {
            return Err("Missing audio file");
        }
    }

    info!("All boot up checks completed successfully!");
    Ok(())
}

fn main() {
    SimpleLogger::new().init().unwrap();

    let mut connection = establish_connection();
    let result = boot_checks(&mut connection);
    match result {
        Ok(_) => (),
        Err(msg) => {
            error!("Boot check failed: {:?}", msg);
            exit(1);
        }
    }

    let mut actions: VecDeque<action::Action> = VecDeque::new();
    actions.push_back(action::Action::WaitForAll(vec![
        action::Action::Wait(Duration::from_secs(2)),
        action::Action::PlayAudio(Track::Beep),
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
