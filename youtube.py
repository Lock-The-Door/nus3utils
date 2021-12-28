from pytube import YouTube

def DownloadAudio(link):
    yt = YouTube(link)
    stream = yt.streams.get_audio_only()