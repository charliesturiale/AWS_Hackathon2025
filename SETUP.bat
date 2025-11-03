@echo off
color 0B
title SafePath - First Time Setup

echo.
echo ========================================================================
echo                     SAFEPATH - FIRST TIME SETUP
echo ========================================================================
echo.
echo  This script will:
echo    1. Check for required software (Python, Node.js)
echo    2. Create Python virtual environment
echo    3. Install backend dependencies
echo    4. Install frontend dependencies
echo    5. Verify .env configuration
echo.
echo  Estimated time: 3-5 minutes
echo.
pause

echo.
echo ========================================================================
echo STEP 1: Checking Required Software
echo ========================================================================
echo.

REM Check Python
echo Checking for Python 3.9+...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.9 or later:
    echo   1. Go to https://www.python.org/downloads/
    echo   2. Download Python 3.9+ for Windows
    echo   3. Run installer and CHECK "Add Python to PATH"
    echo   4. Restart this script after installation
    echo.
    pause
    exit /b 1
)
python --version
echo Python found!
echo.

REM Check Node.js
echo Checking for Node.js 16+...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Node.js is not installed or not in PATH
    echo.
    echo Please install Node.js 16 or later:
    echo   1. Go to https://nodejs.org/
    echo   2. Download LTS version for Windows
    echo   3. Run installer (default options are fine)
    echo   4. Restart this script after installation
    echo.
    pause
    exit /b 1
)
node --version
echo Node.js found!
echo.

REM Check npm
echo Checking for npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] npm not found (should come with Node.js)
    echo Please reinstall Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
npm --version
echo npm found!
echo.

echo All required software is installed!
echo.
pause

echo.
echo ========================================================================
echo STEP 2: Backend Setup (Python Virtual Environment)
echo ========================================================================
echo.

cd "%~dp0backend"

if exist venv (
    echo Virtual environment already exists. Skipping creation...
) else (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to create virtual environment
        echo Make sure Python is properly installed
        pause
        exit /b 1
    )
    echo Virtual environment created!
)
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

echo Installing Python dependencies (this may take a few minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install Python dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)
echo.
echo Backend dependencies installed!
echo.
pause

echo.
echo ========================================================================
echo STEP 3: Frontend Setup (Node.js Dependencies)
echo ========================================================================
echo.

cd "%~dp0frontend"

echo Installing Node.js dependencies (this may take a few minutes)...
call npm install
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install Node.js dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)
echo.
echo Frontend dependencies installed!
echo.
pause

echo.
echo ========================================================================
echo STEP 4: API Keys Configuration
echo ========================================================================
echo.

cd "%~dp0"

if exist .env (
    echo.
    echo .env file already exists!
    echo.
    echo Current configuration:
    type .env
    echo.
    echo.
    set /p "RECONFIGURE=Do you want to reconfigure API keys? (y/n): "
    if /i not "%RECONFIGURE%"=="y" goto skip_env
)

echo.
echo You need API keys to run SafePath:
echo.
echo   1. DataSF API Token (FREE)
echo      - Go to: https://data.sfgov.org/
echo      - Click "Sign Up" to create a free account
echo      - Get your App Token from profile settings
echo.
echo   2. GraphHopper API Key (FREE tier available)
echo      - Go to: https://www.graphhopper.com/
echo      - Click "Get started for free"
echo      - Copy your API key from dashboard
echo.
echo Press any key once you have your API keys ready...
pause >nul
echo.

set /p "DATASF_TOKEN=Enter your DataSF API Token: "
set /p "GRAPHHOPPER_KEY=Enter your GraphHopper API Key: "

echo.
echo Creating .env file with your API keys...
(
echo # DataSF API Token
echo DATASF_API_TOKEN=%DATASF_TOKEN%
echo.
echo # DataSF API Endpoints
echo DATASF_CRIME_API=https://data.sfgov.org/resource/gnap-fj3t.json
echo DATASF_311_API=https://data.sfgov.org/resource/vw6y-z8j6.json
echo.
echo # GraphHopper API Key
echo GRAPHHOPPER_API_KEY=%GRAPHHOPPER_KEY%
echo.
echo # Backend Configuration
echo BACKEND_PORT=8000
echo FRONTEND_URL=http://localhost:3000
echo.
echo # Data Refresh Interval ^(minutes^)
echo DATA_REFRESH_INTERVAL=10
) > .env

echo.
echo .env file created successfully!
echo.

:skip_env

echo.
echo ========================================================================
echo STEP 5: Verification
echo ========================================================================
echo.

echo Running quick verification...
echo.

REM Check backend can import main modules
cd "%~dp0backend"
call venv\Scripts\activate.bat
python -c "from app import main; print('Backend modules OK')" 2>nul
if errorlevel 1 (
    echo [WARNING] Backend module import failed. May need to check dependencies.
) else (
    echo Backend modules: OK
)
echo.

REM Check frontend node_modules
if exist "%~dp0frontend\node_modules" (
    echo Frontend modules: OK
) else (
    echo [WARNING] Frontend node_modules not found
)
echo.

echo.
echo ========================================================================
echo                          SETUP COMPLETE!
echo ========================================================================
echo.
echo  Next steps:
echo    1. Run START_HERE.bat to launch SafePath
echo    2. Wait for both servers to start (takes ~15 seconds)
echo    3. Browser will automatically open to http://localhost:3000
echo.
echo  Testing SafePath:
echo    - Try: "Union Square, SF" to "Ferry Building, SF"
echo    - View multiple safe route options on the map
echo    - Check safety scores and incident data
echo.
echo  Need help?
echo    - Read README.md for detailed documentation
echo    - Check DEPLOYMENT.md for troubleshooting
echo    - Run test-backend.bat to verify backend health
echo.
echo ========================================================================
echo.
pause
exit /b 0
