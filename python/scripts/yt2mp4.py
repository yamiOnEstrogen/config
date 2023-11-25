# This script was made for my Media Server that I am working on #
# Developer: @withervt #
# Created: 11/24/2023 #

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
MAX_RETRIES = 3


def sanitize_filename(title):
    # Replace invalid characters with underscores
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        title = title.replace(char, '_')
    return title

def get_google_api_key():
    api_key_file = "/etc/youtube_api_key"
    if os.path.isfile(api_key_file):
        with open(api_key_file, 'r') as file:
            return file.read().strip()
    else:
        raise ValueError("Google API key file not found at /etc/youtube_api_key")

def get_playlist_title(url):
    api_key = get_google_api_key()
    youtube = build('youtube', 'v3', developerKey=api_key)
    playlist_id = Playlist(url).playlist_id
    request = youtube.playlists().list(
        part="snippet",
        id=playlist_id
    )
    response = request.execute()
    return response['items'][0]['snippet']['localized']['title'] if response['items'] else None

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
                retry_count = 0
                while retry_count < MAX_RETRIES:
                    try:
                        download_single_video(video_url, folder, res, rip_audio)
                        break
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading video: {e}. Retrying...")
                        retry_count += 1
                        time.sleep(5)  # Add a delay of 5 seconds between retries
                if retry_count == MAX_RETRIES:
                    print(f"Max retries reached. Unable to download {video_url}")
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

            # Sanitize the title for creating a valid filename
        title = sanitize_filename(yt.title)

        # If folder is provided, download to that folder
        if folder:
            if rip_audio:
                filepath = os.path.join(folder, f"{title}.mp3")
            else:
                filepath = os.path.join(folder, f"{title}.mp4")
        else:
            if rip_audio:
                filepath = f"{title}.mp3"
            else:
                filepath = f"{title}.mp4"

        response = requests.get(audio_stream.url if rip_audio else video_stream.url, stream=True, timeout=10)  # Set timeout to 10 seconds
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading '{yt.title}' :: {res}") as bar, open(filepath, 'wb') as file:
            for data in response.iter_content(chunk_size=block_size):
                if data:
                    bar.update(len(data))
                    file.write(data)

        print(f"\nDownloaded: {yt.title} at {res}{' (MP3)' if rip_audio else ''}")
    except requests.exceptions.ChunkedEncodingError as e:
        print(f"Error downloading video: {e}. Retrying...")
        download_single_video(url, folder, res, rip_audio)
    except Exception as e:
        print(f"Error downloading video: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos.")
    parser.add_argument("input", help="Video URL or comma-separated list of URLs")
    parser.add_argument("--folder", help="Folder to save downloaded videos")
    parser.add_argument("--resolution", default='1080p', help="Video resolution (default: 1080p)")
    parser.add_argument("--rip-audio", action="store_true", help="Download only the audio in MP3 format")

    args = parser.parse_args()

    if ',' in args.input:
        # If multiple URLs are provided as a comma-separated list
        urls = args.input.split(',')
        for url in urls:
            print(f'Getting info on {url.strip()}')
            download_video(url.strip(), args.folder, args.resolution, args.rip_audio)
    else:
        # If a single URL is provided
        print(f'Getting info on {args.input}')
        download_video(args.input, args.folder, args.resolution, args.rip_audio)

if __name__ == "__main__":
    main()
