@echo off
echo ========================================
echo   SafePath Frontend - Starting...
echo ========================================
echo.

cd /d "%~dp0frontend"

echo [1/2] Checking node_modules...
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    echo Dependencies installed!
) else (
    echo Dependencies found!
)
echo.

echo [2/2] Starting React development server...
echo.
echo ========================================
echo   Frontend running at: http://localhost:3000
echo   Browser will open automatically
echo   Press Ctrl+C to stop
echo ========================================
echo.

call npm start

pause
