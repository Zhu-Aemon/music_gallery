import vlc
import playsound
from pydub import AudioSegment
import os
from pydub.playback import play
from threading import Thread

AudioSegment.converter = os.getcwd() + "\\ffmpeg.exe"
AudioSegment.ffprobe = os.getcwd() + "\\ffprobe.exe"
sound = AudioSegment.from_mp3(r"E:\CloudMusic\Felicity - Burnt Sugar.mp3")

# vlc.MediaPlayer(r"E:\CloudMusic\Abel Korzeniowski - Dance For Me Wallis.mp3").play()
# playsound.playsound(r"E:\CloudMusic\Abel Korzeniowski - Dance For Me Wallis.mp3", True)
# song = AudioSegment.from_mp3(r"E:\CloudMusic\Abel Korzeniowski - Dance For Me Wallis.mp3")
print(sound.duration_seconds)


def play_song():
    while True:
        play(sound)


t = Thread(target=play_song())
t.start()
