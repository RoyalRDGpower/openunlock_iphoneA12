#!/bin/bash
echo "🔓 OpenUnlock Linux - Setup Script"
echo "===================================="

sudo apt-get update

sudo apt-get install -y python3 python3-pip python3-venv libimobiledevice-utils idevicerestore usbmuxd git build-essential libusb-1.0-0-dev

echo "✅ System dependencies installed"

python3 -m venv venv

source venv/bin/activate

pip install PyQt5 pyusb

echo "✅ Python packages installed"

if [ ! -d "ipwndfu" ]; then
    git clone https://github.com/axi0mX/ipwndfu.git
fi

if [ ! -d "palera1n" ]; then
    git clone --recursive https://github.com/palera1n/palera1n.git
fi

mkdir -p logs

echo "===================================="
echo "✅ Setup Complete!"
echo "Now run:"
echo "  source venv/bin/activate"
echo "  python3 main.py"
echo "===================================="
