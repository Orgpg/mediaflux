"""YouTube adapter powered by yt-dlp."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from core.utils import find_ffmpeg_dir

ProgressHook = Callable[[dict], None]


class YouTubeDownloader:
    """Encapsulates all yt-dlp options for YouTube downloads."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def download_video(
        self,
        url: str,
        output_dir: Path,
        quality: str,
        progress_hook: ProgressHook | None = None,
        download_thumbnail: bool = False,
        download_subtitles: bool = False,
        playlist: bool = False,
    ) -> None:
        """Download video media using a quality-aware format selector."""
        ffmpeg_dir = find_ffmpeg_dir()
        has_ffmpeg = ffmpeg_dir is not None
        options = self._base_options(output_dir, progress_hook)
        options.update(
            {
                "format": self._video_format(quality, allow_merge=has_ffmpeg),
                "noplaylist": not playlist,
                "writethumbnail": download_thumbnail,
                "writesubtitles": download_subtitles,
                "writeautomaticsub": download_subtitles,
                "subtitleslangs": ["en"],
            }
        )
        if has_ffmpeg:
            options["merge_output_format"] = "mp4"
            options["ffmpeg_location"] = str(ffmpeg_dir)
        else:
            self.logger.warning("FFmpeg is not available; using a single-file video format.")
        self._run(url, options)

    def download_audio(
        self,
        url: str,
        output_dir: Path,
        bitrate: str = "192",
        progress_hook: ProgressHook | None = None,
    ) -> None:
        """Download audio and use FFmpeg to extract an MP3 file."""
        options = self._base_options(output_dir, progress_hook)
        ffmpeg_dir = find_ffmpeg_dir()
        if ffmpeg_dir is not None:
            options["ffmpeg_location"] = str(ffmpeg_dir)
        options.update(
            {
                "format": "bestaudio/best",
                "noplaylist": False,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": bitrate,
                    }
                ],
            }
        )
        self._run(url, options)

    def _base_options(self, output_dir: Path, progress_hook: ProgressHook | None) -> dict:
        output_template = str(output_dir / "%(title).180s [%(id)s].%(ext)s")
        hooks = [progress_hook] if progress_hook else []
        return {
            "outtmpl": output_template,
            "progress_hooks": hooks,
            "restrictfilenames": True,
            "windowsfilenames": True,
            "ignoreerrors": False,
            "quiet": True,
            "no_warnings": True,
        }

    def _video_format(self, quality: str, allow_merge: bool) -> str:
        """Build a format string that gracefully falls back to best available."""
        if not allow_merge:
            if quality == "best":
                return "best[ext=mp4][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]"
            if quality.isdigit():
                return (
                    f"best[height<={quality}][ext=mp4][vcodec!=none][acodec!=none]/"
                    f"best[height<={quality}][vcodec!=none][acodec!=none]/"
                    "best[ext=mp4][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]"
                )
            self.logger.warning("Unknown quality '%s'; falling back to best.", quality)
            return "best[ext=mp4][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]"

        if quality == "best":
            return (
                "bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/"
                "bv*[ext=mp4]+ba[ext=m4a]/"
                "best[ext=mp4][vcodec!=none][acodec!=none]/"
                "bv*+ba/best[vcodec!=none][acodec!=none]"
            )
        if quality.isdigit():
            return (
                f"bv*[height<={quality}][ext=mp4][vcodec^=avc1]+ba[ext=m4a]/"
                f"bv*[height<={quality}][ext=mp4]+ba[ext=m4a]/"
                f"best[height<={quality}][vcodec!=none][acodec!=none]/"
                f"bv*[height<={quality}]+ba/"
                "best[ext=mp4][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]"
            )
        self.logger.warning("Unknown quality '%s'; falling back to best.", quality)
        return (
            "bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/"
            "best[ext=mp4][vcodec!=none][acodec!=none]/"
            "bv*+ba/best[vcodec!=none][acodec!=none]"
        )

    def _run(self, url: str, options: dict) -> None:
        self.logger.info("Starting yt-dlp download: %s", url)
        try:
            with YoutubeDL(options) as ydl:
                ydl.download([url])
        except DownloadError as exc:
            self.logger.exception("yt-dlp download failed")
            message = str(exc).replace("\x1b[0;31m", "").replace("\x1b[0m", "").strip()
            raise RuntimeError(f"Download failed: {message}") from exc
