"""Cross-platform native file dialogs with terminal fallbacks."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from rich.console import Console

from ui.menu import ask_optional_path

WINDOWS_THIS_PC = "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}"


def choose_url_file(console: Console, initial_dir: Path) -> Path | None:
    """Open a file picker for a URL text file."""
    selected = _ask_open_file(
        title="Select URL text file",
        initial_dir=_default_start_location(initial_dir),
        tkinter_filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        windows_filter="Text files (*.txt)|*.txt|All files (*.*)|*.*",
    )
    if selected:
        return selected

    console.print("[yellow]File picker was closed or unavailable.[/yellow]")
    fallback = ask_optional_path("URL text file path", "required")
    return Path(fallback).expanduser() if fallback else None


def choose_media_file(console: Console, initial_dir: Path) -> Path | None:
    """Open a file picker for a local media file."""
    selected = _ask_open_file(
        title="Select media file",
        initial_dir=_default_start_location(initial_dir),
        tkinter_filetypes=(
            ("Media files", "*.mp4 *.mkv *.mov *.webm *.avi *.mp3 *.wav *.m4a *.flac"),
            ("Video files", "*.mp4 *.mkv *.mov *.webm *.avi"),
            ("Audio files", "*.mp3 *.wav *.m4a *.flac"),
            ("All files", "*.*"),
        ),
        windows_filter=(
            "Media files|*.mp4;*.mkv;*.mov;*.webm;*.avi;*.mp3;*.wav;*.m4a;*.flac|"
            "Video files|*.mp4;*.mkv;*.mov;*.webm;*.avi|"
            "Audio files|*.mp3;*.wav;*.m4a;*.flac|"
            "All files (*.*)|*.*"
        ),
    )
    if selected:
        return selected

    console.print("[yellow]File picker was closed or unavailable.[/yellow]")
    fallback = ask_optional_path("Input media file path", "required")
    return Path(fallback).expanduser() if fallback else None


def choose_output_file(console: Console, initial_dir: Path, default_extension: str) -> Path | None:
    """Open a save dialog for converted output files."""
    selected = _ask_save_file(
        title="Save converted file as",
        initial_dir=_default_output_location(initial_dir),
        default_extension=default_extension,
    )
    if selected:
        return selected

    console.print("[yellow]Save dialog was closed or unavailable. Default outputs folder will be used.[/yellow]")
    return None


def choose_folder(console: Console, title: str, fallback_prompt: str = "Folder path") -> Path | None:
    """Open a folder picker and fall back to terminal input."""
    selected = _ask_folder(title=title, initial_dir=_default_output_location(Path.home()))
    if selected:
        return selected

    console.print("[yellow]Folder picker was closed or unavailable.[/yellow]")
    fallback = ask_optional_path(fallback_prompt, "required")
    return Path(fallback).expanduser() if fallback else None


def _ask_open_file(
    title: str,
    initial_dir: str,
    tkinter_filetypes: tuple[tuple[str, str], ...],
    windows_filter: str,
) -> Path | None:
    if platform.system() == "Windows":
        selected = _ask_open_file_windows(title, initial_dir, windows_filter)
        if selected:
            return selected

    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.update()
        root.attributes("-topmost", True)
        filename = filedialog.askopenfilename(title=title, initialdir=initial_dir, filetypes=tkinter_filetypes)
        root.destroy()
    except Exception:
        return None

    return Path(filename) if filename else None


def _ask_save_file(title: str, initial_dir: str, default_extension: str) -> Path | None:
    suffix = f".{default_extension.lower().lstrip('.')}"
    if platform.system() == "Windows":
        selected = _ask_save_file_windows(title, initial_dir, suffix)
        if selected:
            return selected

    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.update()
        root.attributes("-topmost", True)
        filename = filedialog.asksaveasfilename(
            title=title,
            initialdir=initial_dir,
            defaultextension=suffix,
            filetypes=((f"{suffix.upper()} file", f"*{suffix}"), ("All files", "*.*")),
        )
        root.destroy()
    except Exception:
        return None

    return Path(filename) if filename else None


def _ask_folder(title: str, initial_dir: str) -> Path | None:
    if platform.system() == "Windows":
        selected = _ask_folder_windows(title, initial_dir)
        if selected:
            return selected

    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.update()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title=title, initialdir=initial_dir, mustexist=True)
        root.destroy()
    except Exception:
        return None

    return Path(folder) if folder else None


def _default_start_location(initial_dir: Path) -> str:
    """Return the best native start location for the current OS."""
    if platform.system() == "Windows":
        return WINDOWS_THIS_PC
    if initial_dir.exists():
        return str(initial_dir)
    return str(Path.home())


def _default_output_location(fallback_dir: Path) -> str:
    """Return the default save location for output files and download folders."""
    downloads_dir = Path.home() / "Downloads"
    if downloads_dir.exists():
        return str(downloads_dir)
    if fallback_dir.exists():
        return str(fallback_dir)
    return str(Path.home())


def _ask_open_file_windows(title: str, initial_dir: str, file_filter: str) -> Path | None:
    script = f"""
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title = {title!r}
$dialog.Filter = {file_filter!r}
$dialog.InitialDirectory = {initial_dir!r}
$dialog.CheckFileExists = $true
$dialog.Multiselect = $false
$dialog.RestoreDirectory = $true
$result = $dialog.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    Write-Output $dialog.FileName
}}
"""
    return _run_powershell_dialog(script)


def _ask_save_file_windows(title: str, initial_dir: str, suffix: str) -> Path | None:
    file_filter = f"{suffix.upper()} file (*{suffix})|*{suffix}|All files (*.*)|*.*"
    script = f"""
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.SaveFileDialog
$dialog.Title = {title!r}
$dialog.Filter = {file_filter!r}
$dialog.DefaultExt = {suffix.lstrip('.')!r}
$dialog.InitialDirectory = {initial_dir!r}
$dialog.OverwritePrompt = $true
$dialog.RestoreDirectory = $true
$result = $dialog.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    Write-Output $dialog.FileName
}}
"""
    return _run_powershell_dialog(script)


def _ask_folder_windows(title: str, initial_dir: str) -> Path | None:
    script = f"""
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title = {title!r}
$dialog.InitialDirectory = {initial_dir!r}
$dialog.CheckFileExists = $false
$dialog.CheckPathExists = $true
$dialog.ValidateNames = $false
$dialog.Multiselect = $false
$dialog.RestoreDirectory = $true
$dialog.FileName = "Select this folder"
$dialog.Filter = "Folders|*.folder"
$result = $dialog.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
    $path = [System.IO.Path]::GetDirectoryName($dialog.FileName)
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    Write-Output $path
}}
"""
    return _run_powershell_dialog(script)


def _run_powershell_dialog(script: str) -> Path | None:
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except Exception:
        return None

    filename = completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else ""
    return Path(filename) if filename else None
