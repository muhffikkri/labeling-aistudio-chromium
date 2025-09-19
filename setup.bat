@echo off
REM Skrip ini akan menyiapkan dan menjalankan aplikasi Auto-Labeling.

echo [1/5] Memeriksa keberadaan Python...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo   ERROR: Python tidak ditemukan. Harap install Python 3.8+ dan pastikan ada di PATH.
    pause
    exit /b 1
)
echo   OK: Python ditemukan.

echo.
echo [2/5] Memeriksa dan membuat virtual environment (venv)...
if not exist venv (
    echo   Membuat venv baru...
    python -m venv venv
) else (
    echo   Venv sudah ada.
)

echo.
echo [3/5] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat
echo   OK: Venv diaktifkan.

echo.
echo [4/5] Menginstal atau memperbarui dependensi dari requirements.txt...
pip install -r requirements.txt
echo   OK: Dependensi sudah terinstal.

echo.
echo [5/5] Menjalankan aplikasi GUI...
python src/gui/gui.py

echo.
echo Aplikasi telah ditutup.