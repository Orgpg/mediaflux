"""Terminal banner rendering."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config.settings import APP_VERSION, AUTHOR


def print_banner(console: Console) -> None:
    """Print the MediaFlux ASCII banner with Rich styling."""
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo.txt"
    logo = logo_path.read_text(encoding="utf-8") if logo_path.exists() else "MediaFlux"
    text = Text(logo, style="bold bright_cyan")
    text.append("\nAdvanced Media Downloader & Converter", style="bright_green")
    text.append(f"\nVersion: {APP_VERSION}", style="bright_yellow")
    text.append(f"   Author: {AUTHOR}", style="bright_magenta")
    console.print(Panel.fit(text, border_style="bright_magenta", padding=(1, 2)))
