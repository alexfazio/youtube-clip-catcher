<div align="center">
  
![YouTube-clips-banner-new.png](images/YouTube-clips-banner-new.png)

</div>

# youtube-clip-catcher

`youtube-clip-catcher` is a Python script designed to fetch and display metadata of a [YouTube clip](https://support.google.com/youtube/answer/10332730?hl=en-GB&co=GENIE.Platform%3DDesktop&sjid=4705461715572754039-EU) (not a full YouTube video) and download it with custom buffered start and end times. 

Given a YouTube clip URL, e.g. `https://www.youtube.com/clip/<clip-id>` this script queries the YouTube [APIs](https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com) to obtain the start and end time codes of the sub-clip in relation to the full video and downloads only that specific segment.

## Features

- Fetches video details using YouTube API.
- Extracts start and end times of YouTube clips in relation to the full video.
- The specified segment of the video is downloaded using `yt-dlp` for the download process and `ffmpeg` for extraction.

## Example

Given a YouTube clip URL:

```
https://youtube.com/clip/UgkxYimXng8oFu_jEOyBKr5Lx2lv8ELOKcHy?si=bVLQt1Bdnk8AkusH
```

The script will return the start and end times of the sub-clip in relation to the full video and download that segment.

## Usage

1. Clone the repository:
```
git clone https://github.com/yourusername/youtube-clip-catcher.git
```

2. Install the dependencies:

```sh
poetry install
```

3. [YouTube Data API v3](https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com)

Next, you need to create a `.env` file in the root directory of the project. This file will store your YouTube Data API v3 key. Use the following command to create and add your API key to the `.env` file:

```bash
echo "API_KEY=<your-key>" > .env
```

Ensure your `.env` file contains your `API_KEY` key in this format:

```plaintext
API_KEY=<your-key>
```

4. Run the script:
```sh
poetry run python main.py
```

5. Follow the prompts to enter the YouTube clip URL and download the specified segment.

## Configuration

The script uses a configuration file `config.json` to set the desired video buffer:
```json:youtube-clip-catcher/config.json
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
