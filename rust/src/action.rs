use log::info;
use rodio::{Decoder, OutputStream, Sink};
use std::fs::File;
use std::io::BufReader;
use std::thread::{self, sleep, JoinHandle};
use std::time::Duration;

pub enum Action {
    Wait(Duration),
    PlayAudio(String),
    WaitForAll(Vec<Action>),
}

pub fn execute_action(action: Action) {
    match action {
        Action::Wait(duration) => {
            info!("Waiting for {:?}", duration);
            sleep(duration);
            info!("Waited {:?}", duration);
        }
        Action::PlayAudio(filename) => {
            info!("Playing the audio file {}", filename);
            play_audio(&filename);
            info!("Played the audio file {}", filename);
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

fn play_audio(filename: &String) {
    let (_stream, stream_handle) = OutputStream::try_default().unwrap();
    let sink = Sink::try_new(&stream_handle).unwrap();
    let file = BufReader::new(File::open(filename).unwrap());
    let source = Decoder::new(file).unwrap();
    sink.append(source);
    sink.sleep_until_end();
}
