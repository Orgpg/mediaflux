"""Rich progress bridge for yt-dlp hooks."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
)


class DownloadProgress:
    """Context manager that turns yt-dlp hook updates into Rich progress bars."""

    def __init__(self, console: Console) -> None:
        self.progress = Progress(
            TextColumn("[bold bright_green]{task.description}"),
            TextColumn("[cyan]{task.fields[filename]}", justify="left"),
            BarColumn(bar_width=34, complete_style="bright_green", finished_style="green", pulse_style="bright_cyan"),
            TaskProgressColumn(),
            console=console,
            transient=False,
            expand=False,
            refresh_per_second=8,
        )
        self._task_id: TaskID | None = None

    def __enter__(self) -> "DownloadProgress":
        self.progress.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.progress.__exit__(exc_type, exc, tb)

    def hook(self, data: dict) -> None:
        """Receive yt-dlp progress dictionaries."""
        filename = Path(data.get("filename") or data.get("tmpfilename") or "media").name
        status = data.get("status")

        if self._task_id is None:
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            self._task_id = self.progress.add_task("Downloading", filename=_shorten(filename), total=total or None)

        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            self.progress.update(
                self._task_id,
                description="Downloading",
                filename=_shorten(filename),
                total=total or None,
                completed=downloaded,
            )
        elif status == "finished":
            total = data.get("total_bytes") or data.get("downloaded_bytes")
            self.progress.update(
                self._task_id,
                description="Processing",
                total=total or None,
                completed=total or 0,
                filename=_shorten(filename),
            )


def _shorten(filename: str, max_length: int = 42) -> str:
    """Keep long media filenames readable inside the terminal."""
    if len(filename) <= max_length:
        return filename
    return f"{filename[:18]}...{filename[-21:]}"
