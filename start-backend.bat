@echo off
echo ========================================
echo   SafePath Backend - Starting...
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/3] Checking virtual environment...
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment found!
)
echo.

echo [2/3] Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt --quiet
echo Dependencies installed!
echo.

echo [3/3] Starting FastAPI server...
echo.
echo ========================================
echo   Backend running at: http://localhost:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.

REM Set Python to UTF-8 mode to avoid Windows console encoding issues
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

cd app
REM Note: --reload disabled on Windows due to file watcher compatibility issues
python -X utf8 -m uvicorn main:app --port 8000

pause
