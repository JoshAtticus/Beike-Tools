# Installation & Prerequisites

To use the AtticatROM build system, you need a macOS or Linux environment.

## 1. Install Dependencies
You need homebrew (https://brew.sh) installed.

```bash
# Install required libraries
brew install libusb pkg-config dtc squashfs

# Install ImageMagick (needed for icon resizing)
brew install imagemagick
```

## 2. Install sunxi-tools

This project relies on sunxi-fel to flash the camera over USB. You cannot install this directly via brew; you must compile it from source.

Source: https://github.com/linux-sunxi/sunxi-tools

```bash
# 1. Clone the repo
git clone https://github.com/linux-sunxi/sunxi-tools
cd sunxi-tools

# 2. Compile (Apple Silicon / M1 / M2 / M3 fix)
# We need to explicitly point to Homebrew libraries
export CFLAGS="-I$(brew --prefix libusb)/include -I$(brew --prefix dtc)/include"
export LDFLAGS="-L$(brew --prefix libusb)/lib -L$(brew --prefix dtc)/lib"
make

# 3. Verify
./sunxi-fel version
```

# ADB
You need ADB for pushing logos, adb shell, data partition stuff etc

```bash
brew install android-platform-tools
```