@echo off
REM Quick backend health check script

echo.
echo Checking if SafePath backend is running...
echo.

curl -s http://localhost:8000/api/health > nul 2>&1

if %errorlevel% equ 0 (
    echo ================================================================================
    echo SUCCESS: Backend is running and healthy!
    echo ================================================================================
    echo.
    echo Backend health check:
    curl -s http://localhost:8000/api/health
    echo.
    echo.
    echo ================================================================================
    echo BACKEND IS READY FOR TESTING
    echo ================================================================================
    echo.
    echo You can now run tests:
    echo   Option 1: Double-click RUN_TESTS.bat
    echo   Option 2: Run manually:
    echo             cd backend
    echo             python test_route_optimization.py
    echo             python production_test_suite.py
    echo.
) else (
    echo ================================================================================
    echo Backend is NOT running or not ready yet
    echo ================================================================================
    echo.
    echo If you just started it, wait 10-30 seconds and run this script again.
    echo.
    echo To start the backend:
    echo   1. Open PowerShell
    echo   2. cd C:\Users\natha\AWS_Hackathon2025
    echo   3. .\venv\Scripts\Activate.ps1
    echo   4. cd backend\app
    echo   5. python -m uvicorn main:app --port 8000
    echo.
    echo Then run this script again to verify.
    echo.
)

pause
