@echo off
REM Build a single-file Windows executable using PyInstaller.
REM Usage: Open a Developer Command Prompt / CMD in the repo and run: build_exe.bat

REM Activate virtualenv if present
if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
)

echo Installing/Upgrading PyInstaller...
pip install --upgrade pyinstaller

echo Running PyInstaller (this may take a few minutes)...
pyinstaller --noconfirm --onefile --add-data "config;config" --add-data "assets;assets" --add-data "platforms;platforms" --add-binary "tools\ffmpeg\bin;ffmpeg" app.py

echo.
echo Build finished. See the "dist" folder for the generated executable.
echo If ffmpeg is required at runtime, ensure it is distributed or available on PATH.
pause
