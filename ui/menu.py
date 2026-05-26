"""Interactive menu helpers for beginner-friendly CMD workflows."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

VIDEO_QUALITY_OPTIONS = {
    "1": ("Best available", "best"),
    "2": ("2160p / 4K", "2160"),
    "3": ("1440p / 2K", "1440"),
    "4": ("1080p / Full HD", "1080"),
    "5": ("720p / HD", "720"),
    "6": ("480p", "480"),
    "7": ("360p", "360"),
}

MP3_QUALITY_OPTIONS = {
    "1": ("128 kbps", "128"),
    "2": ("192 kbps", "192"),
    "3": ("256 kbps", "256"),
    "4": ("320 kbps", "320"),
}


def ask_download_mode(console: Console) -> str:
    """Ask the user which media mode to use."""
    console.print("[cyan]Choose download mode[/cyan]")
    return Prompt.ask("Mode", choices=["video", "mp3", "playlist"], default="video")


def show_main_menu(console: Console) -> str:
    """Render the main MediaFlux menu and return the selected option."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold bright_cyan", justify="right")
    table.add_column(style="white")
    table.add_row("1", "Download YouTube video")
    table.add_row("2", "Download YouTube audio as MP3")
    table.add_row("3", "Download YouTube playlist")
    table.add_row("4", "Batch download from URL text file")
    table.add_row("5", "Convert local media file")
    table.add_row("6", "System doctor")
    table.add_row("7", "Check for update")
    table.add_row("0", "Exit")

    console.print(Panel(table, title="[bold bright_green]MediaFlux CMD Menu[/bold bright_green]", border_style="bright_cyan"))
    return Prompt.ask("[bold cyan]Select function[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "0"], default="1")


def ask_url(label: str = "URL") -> str:
    """Ask for a media URL."""
    return Prompt.ask(f"[bold cyan]{label}[/bold cyan]").strip()


def ask_quality(default: str = "best") -> str:
    """Ask for a video quality value."""
    return Prompt.ask(
        "[bold cyan]Quality[/bold cyan] [dim](best, 2160, 1440, 1080, 720, 480, 360)[/dim]",
        default=default,
    ).strip()


def ask_video_quality_choice(console: Console) -> str:
    """Ask for video quality using a numbered menu."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold bright_cyan", justify="right")
    table.add_column(style="white")
    table.add_column(style="bright_green")
    for number, (label, value) in VIDEO_QUALITY_OPTIONS.items():
        table.add_row(number, label, value)

    console.print(Panel(table, title="[bold bright_green]Video Quality[/bold bright_green]", border_style="bright_cyan"))
    choice = Prompt.ask("[bold cyan]Select quality no.[/bold cyan]", choices=list(VIDEO_QUALITY_OPTIONS), default="1")
    return VIDEO_QUALITY_OPTIONS[choice][1]


def ask_audio_bitrate(default: str = "192") -> str:
    """Ask for an MP3 bitrate."""
    return Prompt.ask("[bold cyan]MP3 bitrate[/bold cyan] [dim](128, 192, 256, 320)[/dim]", default=default).strip()


def ask_audio_quality_choice(console: Console) -> str:
    """Ask for MP3 quality using a numbered menu."""
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold bright_cyan", justify="right")
    table.add_column(style="white")
    table.add_column(style="bright_green")
    for number, (label, value) in MP3_QUALITY_OPTIONS.items():
        table.add_row(number, label, value)

    console.print(Panel(table, title="[bold bright_green]MP3 Quality[/bold bright_green]", border_style="bright_cyan"))
    choice = Prompt.ask("[bold cyan]Select quality no.[/bold cyan]", choices=list(MP3_QUALITY_OPTIONS), default="2")
    return MP3_QUALITY_OPTIONS[choice][1]


def ask_optional_path(prompt: str, default_label: str = "press Enter to skip") -> str:
    """Ask for an optional path and return an empty string when skipped."""
    return Prompt.ask(f"[bold cyan]{prompt}[/bold cyan] [dim]({default_label})[/dim]", default="").strip()


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Ask for a yes/no value."""
    return Confirm.ask(f"[bold cyan]{prompt}[/bold cyan]", default=default)
