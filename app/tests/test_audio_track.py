from audio_track import AudioTrack
from os.path import exists, join


def test_audio_tracks_exist():
    for track in AudioTrack:
        assert exists(join("audio", track.value))
