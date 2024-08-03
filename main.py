import re
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import parse_qs, urlparse
from segment_downloader import download_clip  # Import the new function
from dotenv import load_dotenv
import os
import json
from rich.console import Console
from rich.panel import Panel
# from rich.syntax import Syntax
# from rich.markdown import Markdown
# from rich.console import Console

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
    print(f"\nExtracting IDs from URL: {url}")
    parsed_url = urlparse(url)
    print(f"Parsed URL: {parsed_url}")

    # Extract video ID
    if 'v' in parse_qs(parsed_url.query):
        video_id = parse_qs(parsed_url.query)['v'][0]
        print(f"Video ID extracted from query parameter: {video_id}")
    elif 'clip' in parsed_url.path:
        print("Clip URL detected, fetching page to extract video ID")
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")
        video_match = re.search(r'"videoId":"([\w-]{11})"', response.text)
        video_id = video_match.group(1) if video_match else None
        print(f"Video ID extracted from page content: {video_id}")
    else:
        video_id = None
        print("No video ID found in URL")

    # Extract clip ID
    clip_match = re.search(r'clip/([\w-]+)', url)
    clip_id = clip_match.group(1) if clip_match else None
    print(f"Clip ID extracted: {clip_id}")

    return video_id, clip_id


def get_clip_times(clip_id):
    url = f"https://www.youtube.com/clip/{clip_id}"
    print(f"\nFetching clip times from URL: {url}")
    response = requests.get(url)
    print(f"Response status code: {response.status_code}")
    
    # Save the entire response to a file
    output_dir = "response_logs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"clip_{clip_id}_response.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"Full response saved to: {output_file}")
    
    # Look for the specific clipConfig pattern
    clip_config_pattern = re.compile(r'"clipConfig":\s*{[^}]*"startTimeMs":"(\d+)"[^}]*"endTimeMs":"(\d+)"')
    match = clip_config_pattern.search(response.text)

    if match:
        start_ms = int(match.group(1))
        end_ms = int(match.group(2))
        # Convert milliseconds to seconds
        start_time = start_ms / 1000
        end_time = end_ms / 1000

        print("\nExtracted clip times:")
        print(f"Original start time: {start_time:.2f} seconds")
        print(f"Original end time: {end_time:.2f} seconds")

        # Ask user if they want to apply a buffer
        apply_buffer = input("Do you want to apply a buffer time before and after the clip? (y/n): ").lower() == 'y'

        if apply_buffer:
            buffer_time = float(input("Enter the buffer time in seconds: "))
            buffered_start = max(0, start_time - buffer_time)
            buffered_end = end_time + buffer_time

            print(f"Buffered start time: {buffered_start:.2f} seconds")
            print(f"Buffered end time: {buffered_end:.2f} seconds")
        else:
            buffered_start = start_time
            buffered_end = end_time
            print("No buffer applied.")

        return start_time, end_time, buffered_start, buffered_end
    
    print("Failed to extract clip times")
    return None, None, None, None


def get_video_details(youtube, video_id):
    try:
        print(f"\n[youTube-clip-catcher] Fetching video details for video ID: {video_id}")
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics,status",
            id=video_id
        ).execute()

        print("Full API Response:")
        print(json.dumps(response, indent=2))

        if 'items' in response and len(response['items']) > 0:
            video = response['items'][0]
            
            print("\nExtracted Video Details:")
            print(f"Title: {video['snippet']['title']}")
            print(f"Duration: {video['contentDetails']['duration']}")
            print(f"Published At: {video['snippet']['publishedAt']}")
            print(f"Channel Title: {video['snippet']['channelTitle']}")
            print(f"View Count: {video['statistics']['viewCount']}")
            print(f"Like Count: {video['statistics'].get('likeCount', 'N/A')}")
            print(f"Comment Count: {video['statistics'].get('commentCount', 'N/A')}")
            
            print("\nContent Details:")
            for key, value in video['contentDetails'].items():
                print(f"{key}: {value}")
            
            return {
                'title': video['snippet']['title'],
                'duration': video['contentDetails']['duration'],
                'published_at': video['snippet']['publishedAt'],
                'channel_title': video['snippet']['channelTitle'],
                'view_count': video['statistics']['viewCount'],
                'like_count': video['statistics'].get('likeCount', 'N/A'),
                'comment_count': video['statistics'].get('commentCount', 'N/A'),
                'content_details': video['contentDetails']
            }
    except HttpError as e:
        print(f"HttpError occurred: {e}")
        print(f"Error details: {e.error_details}")
        if "API key expired" in str(e):
            print("API key expired. Please renew the API key at console.cloud.google.com")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def format_time(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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

        start_time, end_time, buffered_start, buffered_end = get_clip_times(clip_id)
        if start_time is None or end_time is None:
            print("Failed to fetch clip times. Please try another URL.")
            continue

        print(f"Video Title: {video_details['title']}")
        print(f"Video Duration: {video_details['duration']}")
        print(f"Original Clip Start Time: {start_time:.2f} seconds")
        print(f"Original Clip End Time: {end_time:.2f} seconds")
        print(f"Buffered Clip Start Time: {buffered_start:.2f} seconds")
        print(f"Buffered Clip End Time: {buffered_end:.2f} seconds")

        # Format times for yt-dlp (use buffered times)
        formatted_start = format_time(buffered_start)
        formatted_end = format_time(buffered_end)
        yt_dlp_command = f'yt-dlp --download-sections "*{formatted_start}-{formatted_end}" "https://www.youtube.com/watch?v={video_id}"'
        print(f"\nYou can use the following yt-dlp command to download this clip:")
        print(yt_dlp_command)

        # Ask user if they want to download the clip
        download_choice = input("Do you want to download this clip? (y/n): ").lower()
        if download_choice == 'y':
            output_path = f"output/{video_id}_clip.mp4"
            full_video_url = f"https://www.youtube.com/watch?v={video_id}"

            try:
                downloaded_path = download_clip(full_video_url, buffered_start, buffered_end, output_path)
                if downloaded_path:
                    print(f"Clip successfully downloaded and saved to: {downloaded_path}")
                else:
                    print("Failed to download the clip.")
            except Exception as e:
                print(f"An error occurred while downloading the clip: {e}")
        else:
            print("Clip download skipped.")


if __name__ == "__main__":
    console = Console()
    console.print(Panel("Welcome to the YouTube Clip Downloader & Extender", title="Welcome", style="bold green"))
    console.print("Type 'exit' to end the conversation.")

    main()

#TODO: Change the encoding to H.264.
#TODO: Output the timecode using YT-DLP friendly bash syntax. `yt-dlp --download-sections "*HH:MM:SS-HH:MM:SS" [VIDEO_URL]`