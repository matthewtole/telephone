use crate::database::establish_connection;
use log::info;
use std::thread::{self, sleep};
use std::time::Duration;

use crate::messages::add_message_listen;
use crate::models::Message;

pub enum Action {
    Wait(Duration),
    PlayAudio(String),
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
        Action::PlayAudio(filename) => {
            info!("Playing the audio file {}", filename);
            audio::player::play_tmp(&filename);
            info!("Played the audio file {}", filename);
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

        pub fn play_tmp(filename: &String) {
            play(filename);
        }
    }

    pub mod recorder {
        const SAMPLE_RATE: f64 = 44_100.0;
        const FRAMES: u32 = 256;
        const CHANNELS: i32 = 1;
        const INTERLEAVED: bool = true;

        use log::{debug, info};
        use portaudio::{self, DeviceIndex, Duplex, NonBlocking, PortAudio, Stream};

        pub struct Recording {
            pa: PortAudio,
            input_device: DeviceIndex,
            stream: Stream<NonBlocking, Duplex<f32, f32>>,
        }

        impl Recording {
            pub fn new() -> Result<Self, portaudio::Error> {
                let pa = portaudio::PortAudio::new()?;

                debug!("PortAudio:");
                debug!("version: {}", pa.version());
                debug!("version text: {:?}", pa.version_text());
                debug!("host count: {}", pa.host_api_count()?);

                let default_host = pa.default_host_api()?;
                debug!("default host: {:#?}", pa.host_api_info(default_host));

                let def_input = pa.default_input_device()?;
                let input_info = pa.device_info(def_input)?;
                debug!("Default input device info: {:#?}", &input_info);

                // Construct the input stream parameters.
                let latency = input_info.default_low_input_latency;
                let input_params = portaudio::StreamParameters::<f32>::new(
                    def_input,
                    CHANNELS,
                    INTERLEAVED,
                    latency,
                );

                let input_device = pa.default_output_device()?;
                let output_info = pa.device_info(input_device)?;
                println!("Default output device info: {:#?}", &output_info);

                // Construct the output stream parameters.
                let latency = output_info.default_low_output_latency;
                let output_params =
                    portaudio::StreamParameters::new(input_device, CHANNELS, INTERLEAVED, latency);

                // Check that the stream format is supported.
                pa.is_duplex_format_supported(input_params, output_params, SAMPLE_RATE)?;

                // Construct the settings with which we'll open our duplex stream.
                let settings = portaudio::DuplexStreamSettings::new(
                    input_params,
                    output_params,
                    SAMPLE_RATE,
                    FRAMES,
                );

                // Once the countdown reaches 0 we'll close the stream.
                let mut count_down = 3.0;

                // Keep track of the last `current_time` so we can calculate the delta time.
                let mut maybe_last_time = None;

                // We'll use this channel to send the count_down to the main thread for fun.
                let (sender, receiver) = ::std::sync::mpsc::channel();

                // A callback to pass to the non-blocking stream.
                let callback = move |portaudio::DuplexStreamCallbackArgs {
                                         in_buffer,
                                         out_buffer,
                                         frames,
                                         time,
                                         ..
                                     }| {
                    let current_time = time.current;
                    let prev_time = maybe_last_time.unwrap_or(current_time);
                    let dt = current_time - prev_time;
                    count_down -= dt;
                    maybe_last_time = Some(current_time);

                    assert!(frames == FRAMES as usize);
                    sender.send(count_down).ok();

                    // Pass the input straight to the output - BEWARE OF FEEDBACK!
                    for (output_sample, input_sample) in out_buffer.iter_mut().zip(in_buffer.iter())
                    {
                        *output_sample = *input_sample;
                    }

                    if count_down > 0.0 {
                        portaudio::Continue
                    } else {
                        portaudio::Complete
                    }
                };

                let stream = pa.open_non_blocking_stream(settings, callback)?;

                // Construct a stream with input and output sample types of f32.
                Ok(Self {
                    pa,
                    input_device,
                    stream,
                })
            }

            fn callback(self) {}

            pub fn stop(&mut self) -> Result<(), portaudio::Error> {
                if self.stream.is_stopped()? {
                    info!("Tried to stop an already stopped stream.");
                } else {
                    self.stream.stop()?;
                }
                Ok(())
            }
        }
    }
}
