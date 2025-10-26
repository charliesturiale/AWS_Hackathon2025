@echo off
echo ========================================
echo   SafePath Backend - Health Check
echo ========================================
echo.

echo Testing backend at http://localhost:8000...
echo.

curl -s http://localhost:8000/api/health
if %errorlevel% neq 0 (
    echo.
    echo L ERROR: Backend is not running!
    echo.
    echo Please start the backend first:
    echo    Double-click start-backend.bat
    echo.
) else (
    echo.
    echo.
    echo  Backend is running!
    echo.
    echo Testing route calculation...
    echo.
    curl -s -X POST http://localhost:8000/api/routes -H "Content-Type: application/json" -d "{\"origin\":\"Union Square, San Francisco\",\"destination\":\"Ferry Building, San Francisco\"}"
    echo.
    echo.
    echo  Backend test complete!
)

echo.
pause
