"""Application configuration and filesystem setup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.settings import APP_NAME, PROJECT_ROOT


@dataclass(frozen=True)
class AppConfig:
    """Resolved application paths used by the CLI."""

    app_name: str
    root_dir: Path
    downloads_dir: Path
    outputs_dir: Path
    temp_dir: Path
    logs_dir: Path


def get_config() -> AppConfig:
    """Create required folders and return normalized configuration."""
    config = AppConfig(
        app_name=APP_NAME,
        root_dir=PROJECT_ROOT,
        downloads_dir=PROJECT_ROOT / "downloads",
        outputs_dir=PROJECT_ROOT / "outputs",
        temp_dir=PROJECT_ROOT / "temp",
        logs_dir=PROJECT_ROOT / "logs",
    )

    for directory in (config.downloads_dir, config.outputs_dir, config.temp_dir, config.logs_dir):
        directory.mkdir(parents=True, exist_ok=True)

    return config
