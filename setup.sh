#!/bin/bash
# This script will set up and run the Auto-Labeling Application.
# Requirements: Python 3.8+ installed and accessible via PATH

echo "==============================================="
echo "    AI Studio Auto-Labeling Setup Script"
echo "==============================================="
echo

echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "  ERROR: Python not found. Please install Python 3.8+ and ensure it's in your PATH."
        echo "  Install from: https://www.python.org/downloads/ or your system package manager"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "  OK: $PYTHON_VERSION detected."

echo
echo "[2/5] Checking and creating virtual environment (venv)..."
if [ ! -d "venv" ]; then
    echo "  Creating new virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "  ERROR: Failed to create virtual environment."
        exit 1
    fi
    echo "  OK: Virtual environment created."
else
    echo "  OK: Virtual environment already exists."
fi

echo
echo "[3/5] Activating virtual environment..."
if [ ! -f "venv/bin/activate" ]; then
    echo "  ERROR: Virtual environment activation script not found."
    exit 1
fi
source venv/bin/activate
echo "  OK: Virtual environment activated."

echo
echo "[4/5] Installing or updating dependencies from requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "  ERROR: requirements.txt not found in current directory."
    exit 1
fi
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "  ERROR: Failed to install dependencies."
    echo "  Please check your internet connection and try again."
    exit 1
fi
echo "  OK: Dependencies installed successfully."

echo
echo "[5/5] Starting the GUI application..."
if [ ! -f "src/gui/gui.py" ]; then
    echo "  ERROR: GUI application file not found at src/gui/gui.py"
    echo "  Trying alternative location..."
    if [ ! -f "src/gui.py" ]; then
        echo "  ERROR: GUI application not found. Please check the installation."
        exit 1
    fi
    $PYTHON_CMD src/gui.py
else
    $PYTHON_CMD src/gui/gui.py
fi

echo
echo "==============================================="
echo "    Application has been closed."
echo "    Thank you for using AI Studio Auto-Labeling!"
echo "==============================================="