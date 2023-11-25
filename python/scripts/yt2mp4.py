import os
import sys
import argparse
import requests
from tqdm import tqdm
from pytube import YouTube, Playlist
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

FALLBACK_RES = "720p"
DEFAULT_RES = "1080p"
DEFAULT_FOLDER = None


def get_google_api_key():
    api_key_file = os.path.expanduser("~/.gapi")
    if os.path.isfile(api_key_file):
        with open(api_key_file, 'r') as file:
            return file.read().strip()
    else:
        raise ValueError("Google API key file not found at ~/.gapi")


def get_playlist_title(playlist_url):
    try:
        youtube = build('youtube', 'v3', developerKey=get_google_api_key())
        playlist_id = playlist_url.split("list=")[1]
        request = youtube.playlists().list(part="snippet", id=playlist_id)
        response = request.execute()
        return response['items'][0]['snippet']['title']
    except HttpError as e:
        print(f"Error getting playlist title: {e}")
        return None


def download_video(url, folder=DEFAULT_FOLDER, res=DEFAULT_RES, rip_audio=False):
    try:
        if "playlist" in url.lower():
            playlist_title = get_playlist_title(url)
            if playlist_title is None:
                raise ValueError("Unable to retrieve playlist title.")
            print(f"Playlist Title: {playlist_title}")

            if not folder:
                folder = playlist_title

            # Ensure the folder exists
            os.makedirs(folder, exist_ok=True)

            playlist = Playlist(url)
            for video_url in playlist.video_urls:
                download_single_video(video_url, folder, res, rip_audio)
        else:
            download_single_video(url, folder, res, rip_audio)
    except Exception as e:
        print(f"Error downloading video: {e}")


def download_single_video(url, folder=DEFAULT_FOLDER, res=DEFAULT_RES, rip_audio=False):
    try:
        yt = YouTube(url)
        if rip_audio:
            audio_stream = yt.streams.filter(only_audio=True).first()
            if audio_stream is None:
                raise ValueError("No suitable audio streams found.")
        else:
            video_stream = yt.streams.filter(progressive=True, file_extension="mp4", resolution=res).first()

            if video_stream is None:
                print(f"Video with resolution of '{res}' not available. Downloading with fallback resolution: {FALLBACK_RES}.")
                res = FALLBACK_RES
                video_stream = yt.streams.filter(progressive=True, file_extension="mp4", resolution=FALLBACK_RES).first()

            if video_stream is None:
                raise ValueError("No suitable video streams found.")

        # If folder is provided, download to that folder
        if folder:
            if rip_audio:
                filepath = os.path.join(folder, f"{yt.title}.mp3")
            else:
                filepath = os.path.join(folder, f"{yt.title}.mp4")
        else:
            if rip_audio:
                filepath = f"{yt.title}.mp3"
            else:
                filepath = f"{yt.title}.mp4"

        response = requests.get(audio_stream.url if rip_audio else video_stream.url, stream=True)
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading '{yt.title}' :: {res}") as bar, open(filepath, 'wb') as file:
            for data in response.iter_content(chunk_size=block_size):
                if data:
                    bar.update(len(data))
                    file.write(data)

        print(f"\nDownloaded: {yt.title} at {res}{' (MP3)' if rip_audio else ''}")
    except Exception as e:
        print(f"Error downloading video: {e}")


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos.")
    parser.add_argument("input", help="Video URL or playlist URL")
    parser.add_argument("--folder", help="Folder to save downloaded videos")
    parser.add_argument("--resolution", default='1080p', help="Video resolution (default: 1080p)")
    parser.add_argument("--rip-audio", action="store_true", help="Download only the audio in MP3 format")

    args = parser.parse_args()

    print(f'Getting info on {args.input}')
    download_video(args.input, args.folder, args.resolution, args.rip_audio)


if __name__ == "__main__":
    main()
