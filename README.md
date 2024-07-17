# YT-Clip-Extender

YT-Clip-Extender is a Python script designed to extract and download specific segments of YouTube videos based on YouTube clip URLs. Given a YouTube clip URL, this script queries the YouTube APIs to obtain the start and end time codes of the sub-clip in relation to the full video and downloads only that segment.

## Features

- Extracts start and end times of YouTube clips in relation to the full video.
- Fetches video details using YouTube API.
- Downloads the specified segment of the video using `yt-dlp` and `ffmpeg`.

## Example

Given a YouTube clip URL:

```
https://youtube.com/clip/UgkxYimXng8oFu_jEOyBKr5Lx2lv8ELOKcHy?si=bVLQt1Bdnk8AkusH
```

The script will return the start and end times of the sub-clip in relation to the full video and download that segment.

## Usage

1. Clone the repository:
```
git clone https://github.com/yourusername/YT-Clip-Extender.git
```

2. Install the dependencies:

```sh
poetry install
```

3. Run the script:
```sh
poetry run youtube-clip-info
```

4. Follow the prompts to enter the YouTube clip URL and download the specified segment.

## Configuration

The script uses a configuration file `config.json` to set the desired video buffer:
```json:yt-clip-extender/config.json
{
    "desired_video_buffer": 30
}
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)

## TODOs
- Change the output encoding to H.264.
- Output the timecode using YT-DLP friendly bash syntax. `yt-dlp --download-sections "*HH:MM:SS-HH:MM:SS" [VIDEO_URL]`