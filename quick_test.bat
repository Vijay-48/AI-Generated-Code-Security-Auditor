@echo off
REM Quick test script for Windows
REM Run this to verify the fixes work

echo ============================================
echo Windows Scan Fix - Quick Test
echo ============================================
echo.

echo Step 1: Environment Check
python test_windows_fix.py
if errorlevel 1 (
    echo.
    echo [ERROR] Environment check failed!
    echo Please fix the issues above before proceeding.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Step 2: Debug Scan Test
echo ============================================
python debug_scan.py tests\test_vulnerable.py
if errorlevel 1 (
    echo.
    echo [ERROR] Debug scan failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Step 3: CLI Scan Test
echo ============================================
python -m auditor.cli scan --path tests\test_vulnerable.py

echo.
echo ============================================
echo All Tests Complete!
echo ============================================
echo Your setup is ready for the hackathon demo.
echo.
pause
