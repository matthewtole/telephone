use log::{error, info};
use rodio::{Decoder, OutputStream, Sink};
use simple_logger::SimpleLogger;
use std::fs::File;
use std::io::BufReader;
use std::sync::mpsc;
use std::time::Duration;

#[derive(Debug)]
enum AudioCommand {
    Noop,
    Pause,
    Resume,
    Stop,
}

fn play(filename: &String, rx: mpsc::Receiver<AudioCommand>) {
    let (_stream, stream_handle) = OutputStream::try_default().unwrap();
    let sink = Sink::try_new(&stream_handle).unwrap();
    let file = BufReader::new(File::open(filename).unwrap());
    let source = Decoder::new(file).unwrap();
    sink.append(source);
    loop {
        let maybe_value = rx.try_recv();
        let value = match maybe_value {
            Ok(value) => value,
            Err(_) => AudioCommand::Noop,
        };
        if sink.empty() {
            info!("Finished playing {}", filename);
            break;
        }
        match value {
            AudioCommand::Pause => {
                info!("Pausing {}", filename);
                sink.pause();
            }
            AudioCommand::Resume => {
                info!("Resuming {}", filename);
                sink.play();
            }
            AudioCommand::Stop => {
                info!("Stopping {}", filename);
                sink.stop();
            }
            AudioCommand::Noop => {}
        }
        std::thread::sleep(Duration::from_millis(50));
    }
}

fn main() {
    SimpleLogger::new().init().unwrap();

    let (tx, rx) = mpsc::channel();
    let (tx2, rx2) = mpsc::channel();

    let handle = std::thread::spawn(|| play(&"../audio/intro-01.wav".to_string(), rx));
    let handle2 = std::thread::spawn(|| play(&"../audio/leave-message.wav".to_string(), rx2));

    handle.join().unwrap();
    handle2.join().unwrap();
}
