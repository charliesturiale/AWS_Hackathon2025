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

cd app
uvicorn main:app --reload --port 8000

pause
