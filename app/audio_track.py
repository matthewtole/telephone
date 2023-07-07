from enum import Enum


class AudioTrack(Enum):
    INTRO = "4th/1.wav"
    MENU_1 = "4th/2.wav"
    MENU_2 = "4th/13.wav"
    RECORD_INTRO = "4th/3.wav"
    RECORD_OUTRO = "4th/4.wav"
    BEEP = "beep.wav"
    LISTEN_INTRO = "4th/5.wav"
    LISTEN_OUTRO = "4th/6.wav"
    INVALID_OPTION_1 = "4th/7.wav"
    INVALID_OPTION_2 = "4th/8.wav"
    INVALID_OPTION_3 = "4th/9.wav"
    INVALID_OPTION_4 = "4th/10.wav"
    INVALID_OPTION_5 = "4th/11.wav"
    INVALID_OPTION_6 = "4th/12.wav"

    HOLD_MUSIC = "hold-music-mono.wav"
    HOLD_MESSAGE = "4th/15.wav"

    # DIGIT_0 = "digits/0.wav"
    DIGIT_1 = "digits/1.wav"
    DIGIT_2 = "digits/2.wav"
    DIGIT_3 = "digits/3.wav"
    DIGIT_4 = "digits/4.wav"
    DIGIT_5 = "digits/5.wav"
    DIGIT_6 = "digits/6.wav"
    DIGIT_7 = "digits/7.wav"
    DIGIT_8 = "digits/8.wav"
    DIGIT_9 = "digits/9.wav"


DIGIT_TRACKS = {
    "1": AudioTrack.DIGIT_1,
    "2": AudioTrack.DIGIT_2,
    "3": AudioTrack.DIGIT_3,
    "4": AudioTrack.DIGIT_4,
    "5": AudioTrack.DIGIT_5,
    "6": AudioTrack.DIGIT_6,
    "7": AudioTrack.DIGIT_7,
    "8": AudioTrack.DIGIT_8,
    "9": AudioTrack.DIGIT_9,
}
