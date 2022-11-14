pub mod audio {
    use std::{env, path::Path};
    use strum_macros::EnumIter;

    #[derive(EnumIter, Debug, PartialEq)]
    pub enum Track {
        Intro01,
        LeaveMessage,
        Menu01,
        RecordIntro,
        RecordOutro,
        Beep,
    }

    fn root() -> String {
        env::var("AUDIO_PATH").expect("AUDIO_PATH must be set")
    }

    impl Track {
        fn filename(&self) -> &Path {
            match self {
                Track::Intro01 => Path::new("intro-01.wav"),
                Track::LeaveMessage => Path::new("leave-message.wav"),
                Track::Menu01 => Path::new("menu-1.wav"),
                Track::RecordIntro => Path::new("record-intro.wav"),
                Track::RecordOutro => Path::new("record-outro.wav"),
                Track::Beep => Path::new("beep.wav"),
            }
        }

        pub fn path(&self) -> String {
            String::from(
                Path::new(root().as_str())
                    .join(self.filename())
                    .to_str()
                    .expect("Failed to convert into a string"),
            )
        }
    }

    pub fn digit_path(num: i8) -> String {
        String::from(
            Path::new(root().as_str())
                .join("digits")
                .join(Path::new(&format!("{}.wav", num)))
                .to_str()
                .expect("Failed to convert into a string"),
        )
    }
}
