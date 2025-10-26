@echo off
color 0A
echo.
echo ========================================================================
echo.
echo                        SAFEPATH APPLICATION
echo              Find the Safest Walking Paths in San Francisco
echo                     AWS INRIX Hackathon 2025
echo.
echo ========================================================================
echo.
echo  This script will start BOTH the backend and frontend servers
echo  in separate windows.
echo.
echo  What will happen:
echo    1. Backend window opens  - FastAPI server (Port 8000)
echo    2. Frontend window opens - React app (Port 3000)
echo    3. Browser opens automatically to http://localhost:3000
echo.
echo  IMPORTANT: Keep both windows open while using the app!
echo.
echo  FEATURES:
echo    - Real-time crime and 311 incident markers on map
echo    - Smart address autocomplete as you type
echo    - Multiple route options with safety scores
echo    - San Francisco focused with live data
echo.
echo ========================================================================
echo.
pause

echo.
echo [1/2] Starting Backend Server...
start "SafePath Backend" cmd /k "%~dp0start-backend.bat"
echo Backend window opened!
echo.

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul
echo.

echo [2/2] Starting Frontend Server...
start "SafePath Frontend" cmd /k "%~dp0start-frontend.bat"
echo Frontend window opened!
echo.

echo ========================================================================
echo.
echo   BOTH SERVERS STARTING!
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000 (opening in browser...)
echo.
echo  To stop: Close both server windows or press Ctrl+C in each
echo.
echo  Enjoy SafePath!
echo.
echo ========================================================================
echo.

timeout /t 3 >nul
start http://localhost:3000

echo.
echo This window can be closed. Keep the server windows open!
echo.
pause
