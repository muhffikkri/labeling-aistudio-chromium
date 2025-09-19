@echo off
REM This script will set up and run the Auto-Labeling Application.
REM Requirements: Python 3.8+ installed and accessible via PATH

echo ===============================================
echo     AI Studio Auto-Labeling Setup Script
echo ===============================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo   ERROR: Python not found. Please install Python 3.8+ and ensure it's in your PATH.
    echo   Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   OK: %%i detected.

echo.
echo [2/5] Checking and creating virtual environment (venv)...
if not exist venv (
    echo   Creating new virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo   ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   OK: Virtual environment created.
) else (
    echo   OK: Virtual environment already exists.
)

echo.
echo [3/5] Activating virtual environment...
if not exist venv\Scripts\activate.bat (
    echo   ERROR: Virtual environment activation script not found.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
echo   OK: Virtual environment activated.

echo.
echo [4/5] Installing or updating dependencies from requirements.txt...
if not exist requirements.txt (
    echo   ERROR: requirements.txt not found in current directory.
    pause
    exit /b 1
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo   ERROR: Failed to install dependencies.
    echo   Please check your internet connection and try again.
    pause
    exit /b 1
)
echo   OK: Dependencies installed successfully.

echo.
echo [5/5] Starting the GUI application...
if not exist src\gui\gui.py (
    echo   ERROR: GUI application file not found at src\gui\gui.py
    echo   Trying alternative location...
    if not exist src\gui.py (
        echo   ERROR: GUI application not found. Please check the installation.
        pause
        exit /b 1
    )
    python src\gui.py
) else (
    python src\gui\gui.py
)

echo.
echo ===============================================
echo     Application has been closed.
echo     Thank you for using AI Studio Auto-Labeling!
echo ===============================================
pause