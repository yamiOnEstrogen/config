import sys
import argparse
import requests
from tqdm import tqdm
from pytube import YouTube, Playlist


FALLBACK_RES = "720p"
DEFAULT_RES = "1080p"
DEFAULT_FOLDER = None


def download_video(url, folder=DEFAULT_FOLDER, res=DEFAULT_RES):
    try:
        if "playlist" in url.lower():
            playlist = Playlist(url)
            for video_url in playlist.video_urls:
                download_single_video(video_url, folder, res)
        else:
            download_single_video(url, folder, res)
    except Exception as e:
        print(f"Error downloading video: {e}")


def download_single_video(url, folder=DEFAULT_FOLDER, res=DEFAULT_RES):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension="mp4", resolution=res).first()

        if video is None:
            print(f"Video with resolution of '{res}' not available. Downloading with fallback resolution: {FALLBACK_RES}.")
            res = FALLBACK_RES
            video = yt.streams.filter(progressive=True, file_extension="mp4", resolution=FALLBACK_RES).first()

        if video is None:
            raise ValueError("No suitable video streams found.")

        # If folder is provided, download to that folder
        if folder:
            filepath = f"{folder}/{yt.title}.mp4"
        else:
            filepath = f"{yt.title}.mp4"

        response = requests.get(video.url, stream=True)
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading '{yt.title}' :: {res}") as bar, open(filepath, 'wb') as file:
            for data in response.iter_content(chunk_size=block_size):
                if data:
                    bar.update(len(data))
                    file.write(data)

        print(f"\nDownloaded: {yt.title} at {res}")
    except Exception as e:
        print(f"Error downloading video: {e}")


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos.")
    parser.add_argument("input", help="Video URL or playlist URL")
    parser.add_argument("--folder", help="Folder to save downloaded videos")
    parser.add_argument("--resolution", default='1080p', help="Video resolution (default: 1080p)")

    args = parser.parse_args()

    print(f'Getting info on {args.input}')
    download_video(args.input, args.folder, args.resolution)


if __name__ == "__main__":
    main()
