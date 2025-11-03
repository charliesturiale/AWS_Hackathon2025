@echo off
REM SafePath Production Test Suite Runner
REM Run this script to execute all pre-deployment tests

echo.
echo ================================================================================
echo SAFEPATH PRODUCTION TEST SUITE
echo ================================================================================
echo.

REM Check if backend is running
echo [1/5] Checking backend status...
curl -s http://localhost:8000/api/health > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Backend is not running!
    echo.
    echo Please start the backend first:
    echo   1. Open PowerShell
    echo   2. cd C:\Users\natha\AWS_Hackathon2025
    echo   3. .\venv\Scripts\Activate.ps1
    echo   4. cd backend\app
    echo   5. python -m uvicorn main:app --port 8000
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)
echo Backend is running!
echo.

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Change to backend directory
cd backend

REM Run route optimization test
echo [3/5] Running route optimization test (CRITICAL)...
echo ================================================================================
python test_route_optimization.py
set OPT_RESULT=%errorlevel%
echo.
echo.

REM Run comprehensive production test suite
echo [4/5] Running comprehensive production test suite...
echo ================================================================================
python production_test_suite.py
set PROD_RESULT=%errorlevel%
echo.
echo.

REM Summary
echo [5/5] Test Results Summary
echo ================================================================================
echo.

if %OPT_RESULT% equ 0 (
    echo Route Optimization Test: PASSED
) else (
    echo Route Optimization Test: FAILED
)

if %PROD_RESULT% equ 0 (
    echo Production Test Suite: PASSED
) else (
    echo Production Test Suite: NEEDS REVIEW
)

echo.
echo ================================================================================
echo.

if %OPT_RESULT% equ 0 if %PROD_RESULT% equ 0 (
    echo STATUS: ALL TESTS PASSED - READY FOR DEPLOYMENT
    echo.
    echo Next steps:
    echo   1. Review test results in backend\test_results_*.json
    echo   2. Complete manual frontend testing optional
    echo   3. Proceed with production deployment
) else (
    echo STATUS: REVIEW REQUIRED
    echo.
    echo Please review the test output above for failures.
    echo Fix any issues and re-run this script.
)

echo.
echo ================================================================================
pause
