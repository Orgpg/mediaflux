"""High-level downloader service used by CLI commands."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Iterable

from core.config import AppConfig
from platforms.youtube import YouTubeDownloader

ProgressHook = Callable[[dict], None]


class MediaDownloader:
    """Facade for current and future platform downloaders."""

    def __init__(self, config: AppConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger
        self.youtube = YouTubeDownloader(logger)

    def download_video(
        self,
        url: str,
        quality: str = "best",
        output_dir: Path | None = None,
        progress_hook: ProgressHook | None = None,
        download_thumbnail: bool = False,
        download_subtitles: bool = False,
    ) -> None:
        """Download one YouTube video."""
        destination = output_dir or self.config.downloads_dir
        destination.mkdir(parents=True, exist_ok=True)
        self.youtube.download_video(
            url=url,
            output_dir=destination,
            quality=quality,
            progress_hook=progress_hook,
            download_thumbnail=download_thumbnail,
            download_subtitles=download_subtitles,
            playlist=False,
        )

    def download_audio_mp3(
        self,
        url: str,
        bitrate: str = "192",
        output_dir: Path | None = None,
        progress_hook: ProgressHook | None = None,
    ) -> None:
        """Download one YouTube video as MP3 audio."""
        destination = output_dir or self.config.downloads_dir
        destination.mkdir(parents=True, exist_ok=True)
        self.youtube.download_audio(url=url, output_dir=destination, bitrate=bitrate, progress_hook=progress_hook)

    def download_playlist(
        self,
        url: str,
        quality: str = "best",
        output_dir: Path | None = None,
        audio_only: bool = False,
        progress_hook: ProgressHook | None = None,
    ) -> None:
        """Download a YouTube playlist as videos or MP3 files."""
        destination = output_dir or self.config.downloads_dir
        destination.mkdir(parents=True, exist_ok=True)
        if audio_only:
            self.youtube.download_audio(url=url, output_dir=destination, bitrate=quality if quality.isdigit() else "192", progress_hook=progress_hook)
            return
        self.youtube.download_video(url=url, output_dir=destination, quality=quality, progress_hook=progress_hook, playlist=True)

    def download_batch(
        self,
        urls: Iterable[str],
        audio_only: bool = False,
        quality: str = "best",
        progress_hook: ProgressHook | None = None,
    ) -> None:
        """Download multiple URLs sequentially."""
        for url in urls:
            self.logger.info("Batch download started: %s", url)
            if audio_only:
                self.download_audio_mp3(url=url, bitrate=quality if quality.isdigit() else "192", progress_hook=progress_hook)
            else:
                self.download_video(url=url, quality=quality, progress_hook=progress_hook)
