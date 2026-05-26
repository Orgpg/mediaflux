"""Self-update support for packaged MediaFlux releases."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from config.settings import APP_VERSION, REPOSITORY

GITHUB_LATEST_RELEASE_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"


@dataclass(frozen=True)
class ReleaseAsset:
    name: str
    download_url: str


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str
    release_url: str
    asset: ReleaseAsset | None
    is_update_available: bool


def check_for_update() -> UpdateInfo:
    """Fetch the latest GitHub release and compare it with the running version."""
    request = urllib.request.Request(
        GITHUB_LATEST_RELEASE_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "MediaFlux-Updater",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        release = json.loads(response.read().decode("utf-8"))

    latest_version = _clean_version(str(release.get("tag_name") or release.get("name") or "0.0.0"))
    current_version = _clean_version(APP_VERSION)
    asset = _select_asset(release.get("assets", []))

    return UpdateInfo(
        current_version=current_version,
        latest_version=latest_version,
        release_url=str(release.get("html_url") or ""),
        asset=asset,
        is_update_available=_version_tuple(latest_version) > _version_tuple(current_version),
    )


def can_auto_update() -> bool:
    """Return True when the current process is a Windows packaged executable."""
    return bool(getattr(sys, "frozen", False)) and platform.system() == "Windows"


def install_windows_update(asset: ReleaseAsset) -> None:
    """Download a Windows release asset and schedule replacement after this app exits."""
    if not can_auto_update():
        raise RuntimeError("Auto update is only available in the Windows EXE build.")

    current_exe = Path(sys.executable).resolve()
    update_dir = Path(tempfile.mkdtemp(prefix="mediaflux-update-"))
    new_exe = update_dir / asset.name
    _download_file(asset.download_url, new_exe)
    _launch_windows_replacer(current_exe, new_exe, os.getpid())


def _select_asset(assets: list[dict]) -> ReleaseAsset | None:
    system = platform.system()
    if system == "Windows":
        candidates = [asset for asset in assets if "windows" in asset.get("name", "").lower() and asset.get("name", "").lower().endswith(".exe")]
    elif system == "Linux":
        candidates = [asset for asset in assets if "linux" in asset.get("name", "").lower()]
    else:
        candidates = [asset for asset in assets if system.lower() in asset.get("name", "").lower()]

    if not candidates:
        return None

    selected = candidates[0]
    return ReleaseAsset(name=str(selected["name"]), download_url=str(selected["browser_download_url"]))


def _download_file(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "MediaFlux-Updater"})
    with urllib.request.urlopen(request, timeout=300) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)


def _launch_windows_replacer(current_exe: Path, new_exe: Path, parent_pid: int) -> None:
    script = f"""
$ErrorActionPreference = 'Stop'
$parentPid = {parent_pid}
$currentExe = {str(current_exe)!r}
$newExe = {str(new_exe)!r}
$backupExe = "$currentExe.old"
Wait-Process -Id $parentPid -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
if (Test-Path $backupExe) {{ Remove-Item -LiteralPath $backupExe -Force -ErrorAction SilentlyContinue }}
Move-Item -LiteralPath $currentExe -Destination $backupExe -Force
Move-Item -LiteralPath $newExe -Destination $currentExe -Force
Unblock-File -LiteralPath $currentExe -ErrorAction SilentlyContinue
Start-Process -FilePath $currentExe
"""
    subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-Command", script],
        close_fds=True,
    )


def _clean_version(version: str) -> str:
    return version.strip().lstrip("vV")


def _version_tuple(version: str) -> tuple[int, ...]:
    parts = []
    for piece in _clean_version(version).split("."):
        number = ""
        for char in piece:
            if not char.isdigit():
                break
            number += char
        parts.append(int(number or "0"))
    return tuple(parts)
