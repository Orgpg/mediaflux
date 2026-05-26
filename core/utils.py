"""Small reusable helpers."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

from config.settings import BUNDLED_FFMPEG_DIR


def validate_url(url: str) -> bool:
    """Return True when a string looks like an HTTP URL."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def slugify(value: str) -> str:
    """Create a Windows-safe filename fragment."""
    value = re.sub(r"[^\w\s.-]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "_", value).strip("._ ")
    return value or "media"


def check_ffmpeg() -> bool:
    """Check whether FFmpeg is available from the project or PATH."""
    return find_ffmpeg_executable() is not None


def find_ffmpeg_executable() -> Path | None:
    """Return the bundled or system FFmpeg executable path."""
    executable_name = "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"
    bundled = BUNDLED_FFMPEG_DIR / executable_name
    if bundled.exists():
        return bundled

    system = shutil.which("ffmpeg")
    return Path(system) if system else None


def find_ffmpeg_dir() -> Path | None:
    """Return the directory yt-dlp should use for FFmpeg."""
    executable = find_ffmpeg_executable()
    return executable.parent if executable else None


def describe_ffmpeg() -> str:
    """Return a human-friendly FFmpeg status message."""
    executable = find_ffmpeg_executable()
    if executable is None:
        return "[red]missing[/red]"
    if executable.parent == BUNDLED_FFMPEG_DIR:
        return f"[green]bundled[/green] [cyan]{executable}[/cyan]"
    return f"[green]system PATH[/green] [cyan]{executable}[/cyan]"
