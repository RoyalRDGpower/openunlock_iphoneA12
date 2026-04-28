#!/bin/bash
echo "🔓 iUnlock AI - Linux Build Script"
echo "===================================="

# Step 1: Install System Dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv libimobiledevice-utils idevicerestore usbmuxd libusb-1.0-0-dev

# Step 2: Setup Python Env
python3 -m venv venv
source venv/bin/activate
pip install PyQt5 pyusb pyinstaller

# Step 3: Build
pyinstaller --onefile --windowed --name "iUnlock_Pro_Linux" --add-data "core:core" main.py

echo "===================================="
echo "✅ Build Complete! Check the 'dist' folder."
