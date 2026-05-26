"""Local media conversion with ffmpeg-python."""

from __future__ import annotations

import logging
from pathlib import Path

import ffmpeg

from core.config import AppConfig
from core.utils import find_ffmpeg_executable


class MediaConverter:
    """Convert media files into common audio/video formats."""

    def __init__(self, config: AppConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def convert(self, input_file: Path, output_format: str, output_file: Path | None = None) -> Path:
        """Convert a media file and return the generated path."""
        output_format = output_format.lower().lstrip(".")
        target = output_file or self.config.outputs_dir / f"{input_file.stem}.{output_format}"
        target.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info("Converting %s to %s", input_file, target)
        try:
            stream = ffmpeg.input(str(input_file))
            if output_format == "mp3":
                stream = ffmpeg.output(stream, str(target), acodec="libmp3lame", audio_bitrate="192k", vn=None)
            else:
                stream = ffmpeg.output(stream, str(target))
            ffmpeg_executable = find_ffmpeg_executable()
            if ffmpeg_executable is None:
                raise RuntimeError("FFmpeg was not found in tools/ffmpeg/bin or system PATH.")
            ffmpeg.run(stream, cmd=str(ffmpeg_executable), overwrite_output=True, quiet=True)
        except ffmpeg.Error as exc:
            message = exc.stderr.decode("utf-8", errors="ignore") if exc.stderr else str(exc)
            self.logger.exception("FFmpeg conversion failed")
            raise RuntimeError(f"FFmpeg conversion failed: {message}") from exc

        return target
