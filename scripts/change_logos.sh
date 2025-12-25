#!/usr/bin/env bash
set -euo pipefail

# Script to change boot and shutdown logos on device
# Images should be 220x176 pixels, JPEG format (baseline, not progressive)

echo "Logo Changer for Allwinner V3 Action Cameras"
echo "======================="
echo ""
echo "Place your images in this directory:"
echo "  - boot.jpg (for boot logo)"
echo "  - shutdown.jpg (for shutdown logo)"
echo ""
echo "Images should be 220x176 pixels, JPEG format (baseline)."
echo ""

# Check for adb
if ! command -v adb >/dev/null 2>&1; then
    echo "Error: adb not found in PATH. Install Android Debug Bridge."
    exit 1
fi

# Check for images
BOOT_IMAGE=""
SHUTDOWN_IMAGE=""

if [[ -f "boot.jpg" ]]; then
    BOOT_IMAGE="boot.jpg"
    echo "✓ Found boot.jpg"
elif [[ -f "boot.jpeg" ]]; then
    BOOT_IMAGE="boot.jpeg"
    echo "✓ Found boot.jpeg"
fi

if [[ -f "shutdown.jpg" ]]; then
    SHUTDOWN_IMAGE="shutdown.jpg"
    echo "✓ Found shutdown.jpg"
elif [[ -f "shutdown.jpeg" ]]; then
    SHUTDOWN_IMAGE="shutdown.jpeg"
    echo "✓ Found shutdown.jpeg"
fi

if [[ -z "$BOOT_IMAGE" && -z "$SHUTDOWN_IMAGE" ]]; then
    echo ""
    echo "Error: No logo images found. Please create boot.jpg and/or shutdown.jpg"
    exit 1
fi

echo ""

# Target size (128KB)
TARGET_SIZE=131072

# Process boot logo
if [[ -n "$BOOT_IMAGE" ]]; then
    echo "Processing boot logo..."
    cp "$BOOT_IMAGE" boot_logo_new.raw
    
    current_size=$(stat -f%z boot_logo_new.raw 2>/dev/null || stat -c%s boot_logo_new.raw 2>/dev/null)
    
    if (( current_size > TARGET_SIZE )); then
        echo "Error: $BOOT_IMAGE is too large (${current_size} bytes). Must be <= ${TARGET_SIZE} bytes."
        rm -f boot_logo_new.raw
        exit 1
    fi
    
    if (( current_size < TARGET_SIZE )); then
        padding=$((TARGET_SIZE - current_size))
        dd if=/dev/zero bs=1 count=$padding >> boot_logo_new.raw 2>/dev/null
        echo "  Padded to ${TARGET_SIZE} bytes"
    else
        echo "  Already ${TARGET_SIZE} bytes"
    fi
fi

# Process shutdown logo
if [[ -n "$SHUTDOWN_IMAGE" ]]; then
    echo "Processing shutdown logo..."
    cp "$SHUTDOWN_IMAGE" shutdown_logo_new.raw
    
    current_size=$(stat -f%z shutdown_logo_new.raw 2>/dev/null || stat -c%s shutdown_logo_new.raw 2>/dev/null)
    
    if (( current_size > TARGET_SIZE )); then
        echo "Error: $SHUTDOWN_IMAGE is too large (${current_size} bytes). Must be <= ${TARGET_SIZE} bytes."
        rm -f shutdown_logo_new.raw boot_logo_new.raw
        exit 1
    fi
    
    if (( current_size < TARGET_SIZE )); then
        padding=$((TARGET_SIZE - current_size))
        dd if=/dev/zero bs=1 count=$padding >> shutdown_logo_new.raw 2>/dev/null
        echo "  Padded to ${TARGET_SIZE} bytes"
    else
        echo "  Already ${TARGET_SIZE} bytes"
    fi
fi

echo ""
echo "Checking device connection..."
if ! adb devices | grep -q "device$"; then
    echo "Error: No device connected via ADB."
    echo "Please connect your device with USB debugging enabled."
    rm -f boot_logo_new.raw shutdown_logo_new.raw
    exit 1
fi

echo "Device connected!"
echo ""
read -r -p "Ready to flash logos to device? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborting."
    rm -f boot_logo_new.raw shutdown_logo_new.raw
    exit 1
fi

# Flash boot logo
if [[ -n "$BOOT_IMAGE" ]]; then
    echo ""
    echo "Flashing boot logo..."
    adb push boot_logo_new.raw /data/
    adb shell "toolbox dd if=/data/boot_logo_new.raw of=/dev/block/mtdblock4 bs=131072 && sync"
    echo "✓ Boot logo flashed"
fi

# Flash shutdown logo
if [[ -n "$SHUTDOWN_IMAGE" ]]; then
    echo ""
    echo "Flashing shutdown logo..."
    adb push shutdown_logo_new.raw /data/
    adb shell "toolbox dd if=/data/shutdown_logo_new.raw of=/dev/block/mtdblock5 bs=131072 && sync"
    echo "✓ Shutdown logo flashed"
fi

# Cleanup
rm -f boot_logo_new.raw shutdown_logo_new.raw

echo ""
echo "Done! Power cycle your device to see the new logos."
echo "⚠️  DO NOT use 'reboot' command - physically power cycle (remove battery/unplug)"
