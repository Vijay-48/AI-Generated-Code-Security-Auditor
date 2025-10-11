@echo off
REM Quick scan batch file for Windows users

if "%1"=="" (
    echo Usage: scan.bat ^<file_path^>
    echo.
    echo Example:
    echo   scan.bat test_vulnerable.py
    exit /b 1
)

echo 🔍 Scanning %1...
echo.

python quick_scan.py %1

pause
