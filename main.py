import re
import requests
from googleapiclient.discovery import build
from urllib.parse import parse_qs, urlparse
from segment_downloader import download_clip  # Import the new function
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in environment variables")

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

DESIRED_VIDEO_BUFFER = config.get("desired_video_buffer", 30)

def extract_ids(url):
    parsed_url = urlparse(url)

    # Extract video ID
    if 'v' in parse_qs(parsed_url.query):
        video_id = parse_qs(parsed_url.query)['v'][0]
    elif 'clip' in parsed_url.path:
        # For clip URLs, we need to fetch the page to get the video ID
        response = requests.get(url)
        video_match = re.search(r'"videoId":"([\w-]{11})"', response.text)
        video_id = video_match.group(1) if video_match else None
    else:
        video_id = None

    # Extract clip ID
    clip_match = re.search(r'clip/([\w-]+)', url)
    clip_id = clip_match.group(1) if clip_match else None

    return video_id, clip_id


def get_video_details(youtube, video_id):
    try:
        response = youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        ).execute()

        if 'items' in response and len(response['items']) > 0:
            video = response['items'][0]
            return {
                'title': video['snippet']['title'],
                'duration': video['contentDetails']['duration']
            }
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


def get_clip_times(clip_id):
    # This is a workaround as the API doesn't provide clip times
    url = f"https://www.youtube.com/clip/{clip_id}"
    response = requests.get(url)
    start_match = re.search(r'"startTimeMs":"(\d+)"', response.text)
    end_match = re.search(r'"endTimeMs":"(\d+)"', response.text)

    if start_match and end_match:
        start_ms = int(start_match.group(1))
        end_ms = int(end_match.group(1))
        return max(0, (start_ms // 1000) - DESIRED_VIDEO_BUFFER), (end_ms // 1000) + DESIRED_VIDEO_BUFFER
    return None, None


def main():
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    while True:
        url = input("Enter the YouTube clip URL (or 'q' to quit): ")
        if url.lower() == 'q':
            print("Exiting the program.")
            break

        video_id, clip_id = extract_ids(url)
        if not video_id or not clip_id:
            print("Invalid URL format. Please try again.")
            continue

        video_details = get_video_details(youtube, video_id)
        if not video_details:
            print("Failed to fetch video details. Please try another URL.")
            continue

        start_time, end_time = get_clip_times(clip_id)
        if start_time is None or end_time is None:
            print("Failed to fetch clip times. Please try another URL.")
            continue

        print(f"Video Title: {video_details['title']}")
        print(f"Video Duration: {video_details['duration']}")
        print(f"Clip Start Time: {start_time} seconds")
        print(f"Clip End Time: {end_time} seconds")

        # Ask user if they want to download the clip
        download_choice = input("Do you want to download this clip? (y/n): ").lower()
        if download_choice == 'y':
            output_path = f"output/{video_id}_clip.mp4"
            full_video_url = f"https://www.youtube.com/watch?v={video_id}"

            try:
                downloaded_path = download_clip(full_video_url, start_time, end_time, output_path)
                if downloaded_path:
                    print(f"Clip successfully downloaded and saved to: {downloaded_path}")
                else:
                    print("Failed to download the clip.")
            except Exception as e:
                print(f"An error occurred while downloading the clip: {e}")
        else:
            print("Clip download skipped.")


if __name__ == "__main__":
    main()

#TODO: Change the encoding to H.264.
#TODO: Output the timecode using YT-DLP friendly bash syntax. `yt-dlp --download-sections "*HH:MM:SS-HH:MM:SS" [VIDEO_URL]`