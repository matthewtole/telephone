from enum import Enum


class AudioTrack(Enum):
    INTRO = "intro-01.wav"
    LEAVE_MESSAGE = "leave-message.wav"
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
