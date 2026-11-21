@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [ForgeCV] .venv not found. Run: uv sync
    pause
    exit /b 1
)
".venv\Scripts\python.exe" main.py --migrate
".venv\Scripts\python.exe" main.py
if errorlevel 1 pause
