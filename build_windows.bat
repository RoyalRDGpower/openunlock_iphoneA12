@echo off
echo 🔓 iUnlock AI - Windows Build (One-by-One)
echo =========================================

:: Create venv if missing
if not exist venv python -m venv venv

echo 1. Installing PyQt5...
venv\Scripts\python -m pip install PyQt5 --default-timeout=1000

echo 2. Installing PyUSB...
venv\Scripts\python -m pip install pyusb --default-timeout=1000

echo 3. Installing PyInstaller...
venv\Scripts\python -m pip install pyinstaller --default-timeout=1000

echo 🔨 Building...
if exist venv\Scripts\pyinstaller.exe (
    venv\Scripts\pyinstaller --onefile --noconsole --name "iUnlock_Pro_Windows" --add-data "core;core" main.py
    echo ✅ Build Finished! Check the 'dist' folder.
) else (
    echo ❌ Build failed because dependencies are missing.
)

pause
