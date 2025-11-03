@echo off
color 0A
title SafePath - Main Launcher

echo.
echo ========================================================================
echo                        SAFEPATH APPLICATION
echo              Find the Safest Walking Paths in San Francisco
echo ========================================================================
echo.

REM Check if this is first run
if not exist "%~dp0backend\venv" (
    echo.
    echo  FIRST TIME SETUP REQUIRED
    echo.
    echo  It looks like you haven't run setup yet.
    echo  Please run SETUP.bat first to install dependencies.
    echo.
    echo  Press any key to run SETUP now, or close this window to exit.
    pause >nul
    call "%~dp0SETUP.bat"
    if errorlevel 1 (
        echo Setup failed. Please fix errors and try again.
        pause
        exit /b 1
    )
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check for .env file
if not exist "%~dp0.env" (
    echo ERROR: .env file not found
    echo Please run SETUP.bat to configure API keys
    pause
    exit /b 1
)

echo  Dependencies verified!
echo.
echo  Starting SafePath...
echo.
echo  This will open TWO windows:
echo    1. Backend Server  (Port 8000) - Keep open
echo    2. Frontend App    (Port 3000) - Keep open
echo.
echo  Your browser will automatically open to http://localhost:3000
echo.
pause

echo.
echo [1/2] Starting Backend Server...
start "SafePath Backend" cmd /k "%~dp0start-backend.bat"
echo  Backend starting...
echo.

echo Waiting 8 seconds for backend to initialize...
timeout /t 8 /nobreak >nul
echo.

echo [2/2] Starting Frontend Server...
start "SafePath Frontend" cmd /k "%~dp0start-frontend.bat"
echo  Frontend starting...
echo.

echo ========================================================================
echo.
echo   SERVERS STARTING!
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000 (opening in browser...)
echo.
echo  To stop: Close both server windows or press Ctrl+C in each
echo.
echo ========================================================================
echo.

timeout /t 5 >nul
start http://localhost:3000

echo.
echo This window can be closed. Keep the server windows open!
echo.
pause
