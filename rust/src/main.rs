use database::establish_connection;
use rodio::{Decoder, OutputStream, Sink};
use std::fs::File;
use std::io::BufReader;
mod database;
mod messages;
mod models;
mod schema;

fn main() {
    play_audio(String::from("../audio/digits/1.wav"));
    play_audio(String::from("../audio/digits/2.wav"));

    let mut connection = establish_connection();
    messages::create_message(&mut connection, "hello.wav", &100);
    messages::add_message_listen(&mut connection, &1);
    messages::add_message_listen(&mut connection, &1);
}

fn play_audio(filename: String) {
    let (_stream, stream_handle) = OutputStream::try_default().unwrap();
    let sink = Sink::try_new(&stream_handle).unwrap();
    let file = BufReader::new(File::open(filename).unwrap());
    let source = Decoder::new(file).unwrap();
    sink.append(source);
    sink.sleep_until_end();
}
