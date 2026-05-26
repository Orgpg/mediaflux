"""Logging configuration for MediaFlux."""

from __future__ import annotations

import logging
from pathlib import Path

from rich.logging import RichHandler


def setup_logger(logs_dir: Path) -> logging.Logger:
    """Configure file and terminal logging once."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("mediaflux")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(logs_dir / "mediaflux.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

    rich_handler = RichHandler(rich_tracebacks=False, markup=True, show_path=False)
    rich_handler.setLevel(logging.CRITICAL)

    logger.addHandler(file_handler)
    logger.addHandler(rich_handler)
    return logger
