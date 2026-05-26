@echo off
REM Create/activate a virtual environment and run the app in a single terminal window.
REM Usage: Open CMD in the repo folder and run: run_mediaflux_single_terminal.bat

n
if not exist venv (
  echo Creating virtual environment...
  python -m venv venv
  call venv\Scripts\activate.bat
  echo Installing requirements...
  pip install -r requirements.txt
) else (
  call venv\Scripts\activate.bat
)

echo Running MediaFlux...
python app.py
pause
