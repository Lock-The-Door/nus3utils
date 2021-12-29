import os
from multiprocessing import Process

from pytube import YouTube
from pytube import Playlist

def GetTitleFromId(id):
    return YouTube("https://www.youtube.com/watch?v=" + id).title
def GetPlaylistTitleFromId(id):
    return Playlist("https://www.youtube.com/playlist?list=" + id).title

def DownloadAudio(id, path):
    # Create link from id
    link = "https://www.youtube.com/watch?v=" + id

    # Download the audio
    yt = YouTube(link)
    stream = yt.streams.get_audio_only()

    # Show download info
    print("Downloading " + yt.title + "...")
    yt.register_on_progress_callback(lambda stream, chunk, bytes_remaining: print("Downloading " + yt.title + ": " + str(bytes_remaining) + " bytes left..."))
    yt.register_on_complete_callback(lambda stream, filepath: print("Downloaded " + yt.title))

    return stream.download(path, id + ".temp")

def DownloadPlaylist(plId, path):
    # Create link from id
    link = "https://www.youtube.com/playlist?list=" + plId

    # Get playlist info
    pl = Playlist(link)
    print("Downloading " + str(len(pl.video_urls)) + " videos from " + pl.title + "...")

    # Download each video
    jobs = {}
    for video in pl.video_urls:
        # Get video id
        id = video.split('=')[1]

        # Duplicate check
        if id in jobs:
            continue

        # Download the video
        p = Process(target=DownloadAudio, args=(id, path))
        jobs[id] = p
        p.start()

    # Wait for all jobs to finish
    for job in jobs:
        jobs[job].join()

    # Return the list of downloaded audio files
    print("Downloaded " + str(len(jobs)) + " videos from " + pl.title)
    return [os.path.join(path, id + ".temp") for id in jobs]
