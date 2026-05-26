"""Static project settings.

Runtime path creation lives in core.config so this file stays easy to edit.
"""

from __future__ import annotations

from pathlib import Path

APP_NAME = "MediaFlux"
APP_VERSION = "1.0.0"
AUTHOR = "Orgpg"
REPOSITORY = "Orgpg/mediaflux"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_FFMPEG_DIR = PROJECT_ROOT / "tools" / "ffmpeg" / "bin"

SUPPORTED_VIDEO_QUALITIES = ("best", "2160", "1440", "1080", "720", "480", "360")
SUPPORTED_AUDIO_BITRATES = ("128", "192", "256", "320")

AI_FEATURE_PLACEHOLDERS = (
    "AI subtitle generator",
    "AI filename optimizer",
    "AI video summarizer",
)
