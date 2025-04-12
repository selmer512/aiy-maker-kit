#!/bin/bash
set -e

echo
echo "📷 Checking for camera configuration..."
if command -v raspi-config &>/dev/null; then
    CAM=$(sudo raspi-config nonint get_camera)
    if [ "$CAM" -eq 1 ]; then
        sudo raspi-config nonint do_camera 0
        echo "Camera is now enabled. Reboot is required to take effect."
        read -p "Reboot now? (y/n): " answer
        if [[ $answer =~ ^[Yy]$ ]]; then
            sudo reboot
        else
            echo "Reboot later to finish camera enablement."
            exit 0
        fi
    else
        echo "Camera is already enabled."
    fi
else
    echo "Skipping camera check — not running Raspberry Pi OS."
fi

echo
echo "🐍 Forcing Python 3.9 as system default..."
if ! command -v python3.9 &>/dev/null; then
    echo "❌ Python 3.9 is not installed. Please compile and install it first."
    exit 1
fi
sudo ln -sf /usr/local/bin/python3.9 /usr/bin/python3
sudo ln -sf /usr/local/bin/pip3.9 /usr/bin/pip3
echo "✅ Python version: $(python3 --version)"

echo
echo "📦 Adding Coral EdgeTPU repo..."
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl -sSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update --allow-releaseinfo-change

echo
echo "📥 Downloading Coral .deb packages to force install..."
mkdir -p ~/coral-pkgs && cd ~/coral-pkgs

for pkg in \
  libedgetpu1-max \
  python3-pycoral \
  python3-tflite-runtime \
  python3-pyaudio \
  python3-opencv \
  libatlas-base-dev \
  zip unzip; do
    echo "📦 Downloading $pkg..."
    apt-get download "$pkg"
done

echo
echo "🚀 Forcing installation of Coral packages (ignoring version conflicts)..."
sudo dpkg -i --force-all ./*.deb || true
sudo apt-get install -f -y
cd ~
rm -rf ~/coral-pkgs

echo
echo "📚 Installing Python pip packages..."
python3 -m pip install --upgrade pip
python3 -m pip install pynput tflite-support

echo
echo "🧠 Cloning and installing AIY Maker Kit..."
git clone https://github.com/google-coral/aiy-maker-kit
python3 -m pip install ./aiy-maker-kit

echo
echo "⬇️ Downloading example models..."
bash aiy-maker-kit/examples/download_models.sh || true
bash aiy-maker-kit/projects/download_models.sh || true

echo
echo "✅ Coral software setup is complete."
echo "Visit: https://coral.ai/docs for more examples."
