@echo off
REM ===================================================================
REM Repository Cleanup Script (Windows)
REM Removes files that should be in .gitignore
REM ===================================================================

echo ===================================================================
echo Repository Cleanup Script (Windows)
echo ===================================================================
echo.

echo Current Repository Status:
echo -------------------------------------------

REM Count Python cache directories
echo Analyzing Python cache files...
for /f %%i in ('dir /s /b /ad __pycache__ 2^>nul ^| find /c /v ""') do set CACHE_DIRS=%%i
echo Python __pycache__ directories: %CACHE_DIRS%

REM Count .pyc files
echo Analyzing .pyc files...
for /f %%i in ('dir /s /b *.pyc 2^>nul ^| find /c /v ""') do set PYC_FILES=%%i
echo Python .pyc files: %PYC_FILES%

REM Count log files
echo Analyzing log files...
for /f %%i in ('dir /s /b *.log 2^>nul ^| find /c /v ""') do set LOG_FILES=%%i
echo Log files: %LOG_FILES%

echo.
echo -------------------------------------------
echo.

set /p CONFIRM="Do you want to clean these files? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Cleanup cancelled.
    pause
    exit /b 0
)

echo.
echo Starting cleanup...
echo.

REM 1. Remove __pycache__ directories
echo 1. Removing Python cache directories...
for /d /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i" 2>nul
echo    Done: __pycache__ directories removed

REM 2. Remove .pyc files
echo 2. Removing .pyc files...
del /s /q *.pyc 2>nul
echo    Done: .pyc files removed

REM 3. Remove .pyo files
echo 3. Removing .pyo files...
del /s /q *.pyo 2>nul
echo    Done: .pyo files removed

REM 4. Remove log files
echo 4. Removing log files...
del /s /q *.log 2>nul
echo    Done: Log files removed

REM 5. Remove temp files
echo 5. Removing temporary files...
del /s /q *.tmp 2>nul
del /s /q *.temp 2>nul
del /s /q *.bak 2>nul
del /s /q *.backup 2>nul
echo    Done: Temporary files removed

REM 6. Remove Windows-specific files
echo 6. Removing Windows-specific files...
del /s /q Thumbs.db 2>nul
del /s /ah /q desktop.ini 2>nul
echo    Done: Windows files removed

REM 7. Remove build directories
echo 7. Removing build directories...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
for /d /r %%i in (*.egg-info) do @if exist "%%i" rmdir /s /q "%%i" 2>nul
echo    Done: Build directories removed

REM 8. Remove pytest cache
echo 8. Removing pytest cache...
for /d /r %%i in (.pytest_cache) do @if exist "%%i" rmdir /s /q "%%i" 2>nul
if exist .coverage del /q .coverage 2>nul
if exist htmlcov rmdir /s /q htmlcov 2>nul
echo    Done: Test cache removed

echo.
echo ===================================================================
echo Cleanup complete!
echo ===================================================================
echo.

REM Show results
echo After Cleanup Status:
echo -------------------------------------------

REM Count remaining cache files
for /f %%i in ('dir /s /b /ad __pycache__ 2^>nul ^| find /c /v ""') do set CACHE_AFTER=%%i
echo Python __pycache__ directories: %CACHE_AFTER% (was %CACHE_DIRS%)

for /f %%i in ('dir /s /b *.pyc 2^>nul ^| find /c /v ""') do set PYC_AFTER=%%i
echo Python .pyc files: %PYC_AFTER% (was %PYC_FILES%)

for /f %%i in ('dir /s /b *.log 2^>nul ^| find /c /v ""') do set LOG_AFTER=%%i
echo Log files: %LOG_AFTER% (was %LOG_FILES%)

echo.
echo Large directories NOT removed (already in .gitignore):
if exist myenv echo    - myenv\ (virtual environment)
if exist chroma_db echo    - chroma_db\ (vector database)
if exist node_modules echo    - node_modules\ (Node.js packages)
if exist tests\chroma_db echo    - tests\chroma_db\ (test database)

echo.
echo These directories are safe and will not be committed to git.
echo.

echo Next steps:
echo    1. Check git status: git status
echo    2. Remove tracked ignored files: git rm --cached filename
echo    3. Commit changes: git commit -m "Clean up repository"
echo.

pause
