@echo off
echo ========================================
echo AI Code Security Auditor - Windows Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment if it doesn't exist
if not exist myenv (
    echo Creating virtual environment...
    python -m venv myenv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip -q

REM Install dependencies
echo Installing dependencies...
pip install click httpx openai pydantic pydantic-settings python-dotenv -q
pip install langgraph langchain langchain-core chromadb sentence-transformers -q
pip install bandit semgrep rich colorama tqdm -q

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo Quick Start:
echo   1. Make sure you have your GROQ_API_KEY in .env file
echo   2. Run: python quick_scan.py test_vulnerable.py
echo   3. Or:  python -m auditor.cli scan --path test_vulnerable.py
echo.
echo Diagnostic:
echo   Run: python diagnose_issue.py
echo.
pause
