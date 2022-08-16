from tasks import AudioTrack
from os.path import exists, join


def test_audio_tracks():
    for track in AudioTrack:
        print(join("audio", track.value))
        assert exists(join("audio", track.value))
