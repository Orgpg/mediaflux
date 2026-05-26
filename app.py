"""MediaFlux command-line entry point.

Run with:
    python app.py --help
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from config.settings import APP_VERSION
from core.config import get_config
from core.converter import MediaConverter
from core.downloader import MediaDownloader
from core.logger import setup_logger
from core.utils import check_ffmpeg, describe_ffmpeg, validate_url
from ui.banner import print_banner
from ui.file_dialog import choose_folder, choose_media_file, choose_output_file, choose_url_file
from ui.menu import (
    ask_audio_quality_choice,
    ask_optional_path,
    ask_url,
    ask_video_quality_choice,
    ask_yes_no,
    show_main_menu,
)
from ui.progress import DownloadProgress

app = typer.Typer(
    name="mediaflux",
    help="Advanced media downloader and converter CLI.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def _startup() -> tuple[MediaDownloader, MediaConverter]:
    """Prepare directories, logging, and service classes for each command."""
    config = get_config()
    logger = setup_logger(config.logs_dir)
    return MediaDownloader(config, logger), MediaConverter(config, logger)


def _exit_with_error(error: Exception) -> None:
    """Render predictable CLI errors without exposing a Python traceback."""
    console.print(f"[bold red]Error:[/bold red] {error}")
    raise typer.Exit(code=1) from error


def _path_from_input(value: str) -> Path | None:
    """Convert optional menu text input into a Path."""
    return Path(value).expanduser() if value else None


def _ask_required_url(label: str) -> str | None:
    """Ask for a URL, with a clear retry/back choice when it is empty or invalid."""
    while True:
        url = ask_url(label)
        if validate_url(url):
            return url

        message = "Video link is required." if not url else "Invalid URL."
        console.print(f"[bold red]{message}[/bold red]")
        if not ask_yes_no("Enter link again? No = back to menu", default=True):
            return None


def _require_download_folder(output: Path | None, label: str = "Select save folder") -> Path:
    """Ask for the save folder when a download command has no output path."""
    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        return output

    console.print(f"[cyan]{label} before downloading.[/cyan]")
    selected = choose_folder(console, title=label, fallback_prompt="Save folder path")
    if selected is None:
        console.print("[yellow]No save folder selected.[/yellow]")
        raise typer.Exit(code=1)
    selected.mkdir(parents=True, exist_ok=True)
    return selected


def _run_doctor() -> None:
    """Print project and dependency status."""
    config = get_config()
    setup_logger(config.logs_dir)
    console.print("Downloads: [cyan]choose a save folder before each download[/cyan]")
    console.print(f"Outputs:   [cyan]{config.outputs_dir}[/cyan]")
    console.print(f"Logs:      [cyan]{config.logs_dir}[/cyan]")
    console.print(f"FFmpeg:    {describe_ffmpeg()}")


def _interactive_menu() -> None:
    """Run the beginner-friendly interactive CMD menu."""
    config = get_config()

    while True:
        choice = show_main_menu(console)

        if choice == "0":
            console.print("[bold green]Goodbye from MediaFlux.[/bold green]")
            return

        try:
            if choice == "1":
                url = _ask_required_url("YouTube video URL")
                if url is None:
                    console.print("[yellow]Returned to menu.[/yellow]")
                    continue
                quality = ask_video_quality_choice(console)
                output = _require_download_folder(None, "Select folder to save the video")
                thumbnail = ask_yes_no("Download thumbnail too?", default=False)
                subtitles = ask_yes_no("Download subtitles too?", default=False)
                download(url=url, quality=quality, output=output, thumbnail=thumbnail, subtitles=subtitles)

            elif choice == "2":
                url = _ask_required_url("YouTube video URL")
                if url is None:
                    console.print("[yellow]Returned to menu.[/yellow]")
                    continue
                bitrate = ask_audio_quality_choice(console)
                output = _require_download_folder(None, "Select folder to save the MP3")
                mp3(url=url, quality=bitrate, output=output)

            elif choice == "3":
                url = _ask_required_url("YouTube playlist URL")
                if url is None:
                    console.print("[yellow]Returned to menu.[/yellow]")
                    continue
                audio_only = ask_yes_no("Download playlist as MP3?", default=False)
                quality = ask_audio_quality_choice(console) if audio_only else ask_video_quality_choice(console)
                output = _require_download_folder(None, "Select folder to save the playlist")
                playlist(url=url, quality=quality, audio_only=audio_only, output=output)

            elif choice == "4":
                console.print("[cyan]Select your URL text file from the file window.[/cyan]")
                file_path = choose_url_file(console, config.root_dir)
                if file_path is None:
                    console.print("[yellow]No file selected.[/yellow]")
                    continue
                audio_only = ask_yes_no("Download all as MP3?", default=False)
                quality = ask_audio_quality_choice(console) if audio_only else ask_video_quality_choice(console)
                output = _require_download_folder(None, "Select folder to save batch downloads")
                batch(file=file_path, audio_only=audio_only, quality=quality, output=output)

            elif choice == "5":
                console.print("[cyan]Select your input media file from the file window.[/cyan]")
                input_file = choose_media_file(console, config.downloads_dir)
                if input_file is None:
                    console.print("[yellow]No media file selected.[/yellow]")
                    continue
                output_format = ask_optional_path("Output format, for example mp3 or mp4", "Enter = mp3") or "mp3"
                output = None
                if ask_yes_no("Choose output file location?", default=False):
                    output = choose_output_file(console, config.outputs_dir, output_format)
                convert(input_file=input_file, output_format=output_format, output=output)

            elif choice == "6":
                _run_doctor()
        except typer.Exit:
            console.print("[yellow]Returned to menu.[/yellow]")
        except Exception as exc:
            console.print(f"[bold red]Error:[/bold red] {exc}")

        if not ask_yes_no("Do another task?", default=True):
            console.print("[bold green]Goodbye from MediaFlux.[/bold green]")
            return


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version."),
) -> None:
    """Show the banner before command execution."""
    print_banner(console)
    if version:
        console.print(f"[bold cyan]MediaFlux[/bold cyan] version [green]{APP_VERSION}[/green]")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit("Interactive mode started. Use [bold]mediaflux --help[/bold] for direct commands."))
        _interactive_menu()
        raise typer.Exit()


@app.command()
def download(
    url: str = typer.Argument(..., help="YouTube video URL."),
    quality: str = typer.Option("best", "--quality", "-q", help="best, 2160, 1440, 1080, 720, 480, 360"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom download folder."),
    thumbnail: bool = typer.Option(False, "--thumbnail", help="Also download thumbnail."),
    subtitles: bool = typer.Option(False, "--subtitles", help="Also download available subtitles."),
) -> None:
    """Download a YouTube video."""
    if not validate_url(url):
        console.print("[bold red]Invalid URL.[/bold red]")
        raise typer.Exit(code=1)

    try:
        output = _require_download_folder(output, "Select folder to save the video")
        downloader, _ = _startup()
        if not check_ffmpeg():
            console.print(
                "[yellow]FFmpeg not found. Video download will use a single-file format; "
                "higher quality audio/video merging needs FFmpeg.[/yellow]"
            )
        with DownloadProgress(console) as progress:
            downloader.download_video(
                url=url,
                quality=quality,
                output_dir=output,
                progress_hook=progress.hook,
                download_thumbnail=thumbnail,
                download_subtitles=subtitles,
            )
    except Exception as exc:
        _exit_with_error(exc)
    console.print("[bold green]Download complete.[/bold green]")


@app.command()
def mp3(
    url: str = typer.Argument(..., help="YouTube video URL."),
    quality: str = typer.Option("192", "--quality", "-q", help="Audio bitrate: 128, 192, 256, 320."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom download folder."),
) -> None:
    """Download YouTube audio and convert it to MP3."""
    if not validate_url(url):
        console.print("[bold red]Invalid URL.[/bold red]")
        raise typer.Exit(code=1)

    if not check_ffmpeg():
        console.print("[bold red]FFmpeg is required for MP3 extraction. Put it in tools/ffmpeg/bin or install it on PATH.[/bold red]")
        raise typer.Exit(code=1)

    try:
        output = _require_download_folder(output, "Select folder to save the MP3")
        downloader, _ = _startup()
        with DownloadProgress(console) as progress:
            downloader.download_audio_mp3(url=url, bitrate=quality, output_dir=output, progress_hook=progress.hook)
    except Exception as exc:
        _exit_with_error(exc)
    console.print("[bold green]MP3 download complete.[/bold green]")


@app.command()
def playlist(
    url: str = typer.Argument(..., help="YouTube playlist URL."),
    quality: str = typer.Option("best", "--quality", "-q", help="best, 1080, 720, 480, 360"),
    audio_only: bool = typer.Option(False, "--audio", help="Download playlist items as MP3."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom download folder."),
) -> None:
    """Download a YouTube playlist."""
    if audio_only and not check_ffmpeg():
        console.print("[bold red]FFmpeg is required for playlist MP3 extraction. Put it in tools/ffmpeg/bin or install it on PATH.[/bold red]")
        raise typer.Exit(code=1)

    try:
        output = _require_download_folder(output, "Select folder to save the playlist")
        downloader, _ = _startup()
        if not audio_only and not check_ffmpeg():
            console.print(
                "[yellow]FFmpeg not found. Playlist videos will use single-file formats; "
                "higher quality merging needs FFmpeg.[/yellow]"
            )
        with DownloadProgress(console) as progress:
            downloader.download_playlist(
                url=url,
                quality=quality,
                output_dir=output,
                audio_only=audio_only,
                progress_hook=progress.hook,
            )
    except Exception as exc:
        _exit_with_error(exc)
    console.print("[bold green]Playlist download complete.[/bold green]")


@app.command()
def batch(
    file: Path = typer.Argument(..., exists=True, readable=True, help="Text file containing one URL per line."),
    audio_only: bool = typer.Option(False, "--audio", help="Download all URLs as MP3."),
    quality: str = typer.Option("best", "--quality", "-q", help="Video quality or audio bitrate."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom download folder."),
) -> None:
    """Download a batch of URLs from a text file."""
    output = _require_download_folder(output, "Select folder to save batch downloads")
    downloader, _ = _startup()
    urls = [line.strip() for line in file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not urls:
        console.print("[yellow]No URLs found in the batch file.[/yellow]")
        raise typer.Exit()

    if audio_only and not check_ffmpeg():
        console.print("[bold red]FFmpeg is required for batch MP3 extraction. Put it in tools/ffmpeg/bin or install it on PATH.[/bold red]")
        raise typer.Exit(code=1)

    try:
        if not audio_only and not check_ffmpeg():
            console.print(
                "[yellow]FFmpeg not found. Videos will use single-file formats; "
                "higher quality merging needs FFmpeg.[/yellow]"
            )
        with DownloadProgress(console) as progress:
            downloader.download_batch(urls=urls, audio_only=audio_only, quality=quality, output_dir=output, progress_hook=progress.hook)
    except Exception as exc:
        _exit_with_error(exc)
    console.print("[bold green]Batch download complete.[/bold green]")


@app.command()
def convert(
    input_file: Path = typer.Argument(..., exists=True, readable=True, help="Input media file."),
    output_format: str = typer.Argument(..., help="Target format, for example mp3, mp4, webm."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Optional output file path."),
) -> None:
    """Convert a local media file using FFmpeg."""
    if not check_ffmpeg():
        console.print("[bold red]FFmpeg is required for conversion. Put it in tools/ffmpeg/bin or install it on PATH.[/bold red]")
        raise typer.Exit(code=1)

    try:
        _, converter = _startup()
        result = converter.convert(input_file=input_file, output_format=output_format, output_file=output)
    except Exception as exc:
        _exit_with_error(exc)
    console.print(f"[bold green]Converted:[/bold green] {result}")


@app.command()
def doctor() -> None:
    """Check local dependencies and project directories."""
    _run_doctor()


if __name__ == "__main__":
    app()
