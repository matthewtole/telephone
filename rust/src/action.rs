use crate::audio::audio::Track;
use crate::database::establish_connection;
use log::info;
use std::thread::{self, sleep};
use std::time::Duration;

use crate::messages::add_message_listen;
use crate::models::Message;

pub enum Action {
    Wait(Duration),
    PlayAudio(Track),
    WaitForAll(Vec<Action>),
    PlayMessage(Message),
}

pub fn execute_action(action: Action) {
    match action {
        Action::Wait(duration) => {
            info!("Waiting for {:?}", duration);
            sleep(duration);
            info!("Waited {:?}", duration);
        }
        Action::PlayAudio(track) => {
            info!("Playing the audio track {:?}", &track);
            audio::player::play_track(&track);
            info!("Played the audio file {:?}", &track);
        }
        Action::PlayMessage(message) => {
            let mut connection = establish_connection();
            info!("Playing the message {}", message.id);
            audio::player::play_message(&message);
            add_message_listen(&mut connection, &message.id);
            info!("Played the message {}", message.id);
        }
        Action::WaitForAll(actions) => {
            let mut handles = Vec::new();
            for action in actions {
                handles.push(thread::spawn(|| execute_action(action)));
            }
            for handle in handles {
                handle.join();
            }
            info!("Completed the tasks");
        }
    }
}

pub mod audio {
    pub mod player {
        use crate::audio::audio::Track;
        use crate::models::Message;
        use rodio::{Decoder, OutputStream, Sink};
        use std::fs::File;
        use std::io::BufReader;

        #[allow(dead_code)]
        pub fn play_message(message: &Message) {
            play(&message.filename);
        }

        fn play(filename: &String) {
            let (_stream, stream_handle) = OutputStream::try_default().unwrap();
            let sink = Sink::try_new(&stream_handle).unwrap();
            let file = BufReader::new(File::open(filename).unwrap());
            let source = Decoder::new(file).unwrap();
            sink.append(source);
            sink.sleep_until_end();
        }

        pub fn play_track(track: &Track) {
            play(&track.path());
        }
    }
}
