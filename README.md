# MediaFlux

MediaFlux is a modern Python 3.12+ command-line media downloader and converter.
It uses `yt-dlp`, `rich`, `typer`, and `ffmpeg-python` to provide a clean,
Windows-friendly CLI for downloading YouTube videos, extracting MP3 audio, and
converting local media files.

Version: `1.0.0`
Author: `Orgpg`

## Features

- YouTube video downloads with selectable quality
- YouTube audio downloads as MP3
- Playlist downloads
- Thumbnail and subtitle options
- Batch URL downloads from a text file
- Rich terminal banner, progress bars, and readable errors
- File logging to `logs/mediaflux.log`
- Bundled FFmpeg support from `tools/ffmpeg/bin`
- Platform placeholders for TikTok, Facebook, and Instagram

## Project Structure

```text
mediaflux/
|-- app.py
|-- core/
|   |-- config.py
|   |-- converter.py
|   |-- downloader.py
|   |-- logger.py
|   `-- utils.py
|-- platforms/
|   |-- youtube.py
|   |-- tiktok.py
|   |-- facebook.py
|   `-- instagram.py
|-- ui/
|   |-- banner.py
|   |-- menu.py
|   |-- progress.py
|   `-- animations.py
|-- tools/
|   `-- ffmpeg/
|       `-- bin/
|-- downloads/
|-- outputs/
|-- temp/
`-- logs/
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Bundled FFmpeg

MediaFlux can use FFmpeg from inside the project, so other Windows machines do
not need a separate FFmpeg installation.

Put FFmpeg here:

```text
mediaflux/
`-- tools/
    `-- ffmpeg/
        `-- bin/
            |-- ffmpeg.exe
            |-- ffprobe.exe
            `-- ffplay.exe
```

Windows steps:

1. Download `ffmpeg-release-essentials.zip` from `https://www.gyan.dev/ffmpeg/builds/`.
2. Extract the zip file.
3. Open the extracted folder and find its `bin` folder.
4. Copy `ffmpeg.exe`, `ffprobe.exe`, and `ffplay.exe`.
5. Paste them into `mediaflux\tools\ffmpeg\bin\`.
6. Run `python app.py doctor`.

If doctor shows `FFmpeg: bundled ...tools\ffmpeg\bin\ffmpeg.exe`, MediaFlux found it.

For macOS or Linux portable use, place the `ffmpeg` executable in:

```text
mediaflux/tools/ffmpeg/bin/ffmpeg
```

Then run:

```bash
chmod +x tools/ffmpeg/bin/ffmpeg
```

## Usage

Start the interactive CMD menu:

```powershell
python app.py
```

On Windows, you can also double-click:

```text
run_mediaflux.bat
```

Direct commands still work:

```powershell
python app.py download "https://www.youtube.com/watch?v=VIDEO_ID"
python app.py download "https://www.youtube.com/watch?v=VIDEO_ID" --quality 1080
python app.py mp3 "https://www.youtube.com/watch?v=VIDEO_ID" --quality 320
python app.py playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"
python app.py batch urls.txt
python app.py convert downloads\video.mp4 mp3
python app.py doctor
```

## Quality Options

Interactive video quality:

```text
1. Best available
2. 2160p / 4K
3. 1440p / 2K
4. 1080p / Full HD
5. 720p / HD
6. 480p
7. 360p
```

Interactive MP3 quality:

```text
1. 128 kbps
2. 192 kbps
3. 256 kbps
4. 320 kbps
```

## PyInstaller EXE Build

```powershell
pip install pyinstaller
pyinstaller --onefile --name mediaflux app.py
```

If you bundle FFmpeg in `tools/ffmpeg/bin`, the target machine does not need
FFmpeg on its system `Path`.
