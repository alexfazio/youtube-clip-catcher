import os
import subprocess
from yt_dlp import YoutubeDL


def download_clip(video_url, start_time, end_time, output_path):
    """
    Download a clip from a YouTube video using yt-dlp and ffmpeg.

    :param video_url: URL of the YouTube video
    :param start_time: Start time of the clip in seconds
    :param end_time: End time of the clip in seconds
    :param output_path: Path to save the output file
    :return: Path to the downloaded clip
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Download options
    ydl_opts = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': '%(id)s.%(ext)s',
        'noplaylist': True,
        'nocheckcertificate': True,  # Add this line to bypass SSL verification
    }

    # Download the video
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        video_id = info_dict.get("id", None)
        video_ext = info_dict.get("ext", "mp4")

    if not video_id:
        raise ValueError("Failed to extract video ID")

    # Full path of the downloaded video
    full_video_path = f"{video_id}.{video_ext}"

    # Calculate duration
    duration = end_time - start_time

    # Use ffmpeg to trim the video
    ffmpeg_command = [
        "ffmpeg",
        "-i", full_video_path,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c", "copy",
        output_path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Clip saved to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while trimming video: {e}")
        return None
    finally:
        # Clean up the full downloaded video
        if os.path.exists(full_video_path):
            os.remove(full_video_path)

    return output_path


if __name__ == "__main__":
    # Example usage
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    start_time = 30  # Start at 30 seconds
    end_time = 60  # End at 60 seconds
    output_path = "output/clip.mp4"

    download_clip(video_url, start_time, end_time, output_path)