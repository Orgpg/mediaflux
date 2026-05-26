@echo off
setlocal
title MediaFlux
cd /d "%~dp0"

if exist "tools\ffmpeg\bin\ffmpeg.exe" (
    set "PATH=%~dp0tools\ffmpeg\bin;%PATH%"
)

if not exist ".venv\Scripts\python.exe" (
    echo MediaFlux virtual environment was not found.
    echo Run this first:
    echo python -m venv .venv
    echo .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

".venv\Scripts\python.exe" app.py
pause
