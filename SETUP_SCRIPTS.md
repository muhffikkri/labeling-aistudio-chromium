# 🚀 Setup Scripts Documentation

## Overview

The project includes automated setup scripts for easy installation and launching of the AI Studio Auto-Labeling application.

## Available Scripts

### 🪟 Windows: `setup.bat`

Automated setup script for Windows systems.

**Features:**

- ✅ Python version detection and validation
- ✅ Automatic virtual environment creation
- ✅ Dependency installation from requirements.txt
- ✅ Error handling with informative messages
- ✅ Automatic GUI application launch
- ✅ Fallback path detection for GUI location

**Usage:**

```batch
# Method 1: Double-click the file in Windows Explorer
setup.bat

# Method 2: Run from Command Prompt
cd path\to\labeling-aistudio-chromium
setup.bat
```

### 🐧 Linux/macOS: `setup.sh`

Automated setup script for Unix-like systems.

**Features:**

- ✅ Cross-compatible Python detection (python3/python)
- ✅ Automatic virtual environment creation
- ✅ Dependency installation from requirements.txt
- ✅ Error handling with informative messages
- ✅ Automatic GUI application launch
- ✅ Fallback path detection for GUI location

**Usage:**

```bash
# Make executable (first time only)
chmod +x setup.sh

# Run the script
./setup.sh
```

## 🔧 What the Scripts Do

### Step 1: Python Detection

- Checks if Python 3.8+ is installed
- Displays Python version information
- Provides installation guidance if Python is missing

### Step 2: Virtual Environment Setup

- Creates `venv` directory if it doesn't exist
- Reuses existing virtual environment if found
- Handles creation errors gracefully

### Step 3: Environment Activation

- Activates the Python virtual environment
- Ensures proper isolation of dependencies

### Step 4: Dependency Installation

- Installs packages from `requirements.txt`
- Updates existing packages if needed
- Provides error handling for network issues

### Step 5: Application Launch

- Attempts to launch the GUI application
- Tries multiple possible GUI file locations
- Provides clear error messages if GUI is not found

## 🚨 Troubleshooting

### Common Issues

**"Python not found" Error:**

- Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
- Ensure Python is added to your system PATH
- Restart your terminal/command prompt after installation

**"Failed to create virtual environment" Error:**

- Check disk space availability
- Ensure you have write permissions in the directory
- Try running as administrator (Windows) or with sudo (Linux/Mac)

**"Failed to install dependencies" Error:**

- Check your internet connection
- Try running: `pip install --upgrade pip` before running the script
- Some packages may require additional system libraries

**"GUI application not found" Error:**

- Verify the project structure is intact
- Check that `src/gui/gui.py` or `src/gui.py` exists
- Ensure all project files were properly downloaded/cloned

### Manual Recovery

If the automated script fails, you can run the steps manually:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/gui/gui.py
# or try:
python src/gui.py
```

## 💡 Script Advantages

### For Beginners

- **One-click setup**: No need to understand Python environments
- **Clear error messages**: Guidance when things go wrong
- **Cross-platform**: Works on Windows, Linux, and macOS

### For Developers

- **Consistent environment**: Everyone uses the same setup
- **Error handling**: Robust error detection and reporting
- **Flexible paths**: Handles different project structures

### For Production

- **Reliable deployment**: Consistent installation process
- **Error logging**: Clear feedback for troubleshooting
- **Validation checks**: Ensures all prerequisites are met

---

**🎯 The setup scripts provide the fastest way to get the AI Studio Auto-Labeling system up and running!**
