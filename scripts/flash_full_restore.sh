#!/usr/bin/env bash
set -euo pipefail

# Script to flash full restore image to device from sector 0 using sunxi-fel

# Check if we're in sunxi-tools directory or navigate to it
if [[ ! -x "./sunxi-fel" ]]; then
    if [[ -d "sunxi-tools" ]]; then
        cd sunxi-tools
    else
        echo "Error: Cannot find sunxi-tools directory or sunxi-fel executable."
        exit 1
    fi
fi

# Get image file
if [[ -n "${1:-}" ]]; then
    IMAGE="$1"
else
    # List available full_restore_v*.bin files
    shopt -s nullglob
    images=(full_restore_v*.bin)
    shopt -u nullglob
    
    if [[ ${#images[@]} -eq 0 ]]; then
        echo "No full_restore_v*.bin files found in $(pwd)."
        exit 1
    elif [[ ${#images[@]} -eq 1 ]]; then
        IMAGE="${images[0]}"
        echo "Found image: $IMAGE"
    else
        echo "Multiple images found:"
        select img in "${images[@]}"; do
            if [[ -n "$img" ]]; then
                IMAGE="$img"
                break
            fi
        done
    fi
fi

if [[ ! -f "$IMAGE" ]]; then
    echo "Image file '$IMAGE' not found."
    exit 1
fi

img_size=$(wc -c < "$IMAGE" | tr -d '[:space:]')
echo "Image size: ${img_size} bytes"

# Warning message
cat <<EOF

⚠️  WARNING: FULL RESTORE ⚠️

This will flash $IMAGE starting from sector 0.
This will completely overwrite the device's flash storage.

Make sure:
 - You have a backup of any important data
 - This is the correct restore image
 - You understand this will erase everything on the device

EOF

read -r -p "Are you sure you want to continue? Type 'yes' to proceed: " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "Aborting."
    exit 1
fi

# Prompt user to enter recovery mode
cat <<EOF

Please enter recovery mode on your device:
 - Remove battery and SD card
 - Hold VOLUME UP
 - While holding VOLUME UP, insert USB cable to host

When the device is in FEL/recovery mode, press ENTER to continue.
EOF

read -r -p "Ready? Press ENTER to flash or Ctrl-C to abort..."

# Flash using sunxi-fel from sector 0
if [[ ! -x "./sunxi-fel" ]]; then
    echo "./sunxi-fel not found or not executable in $(pwd)."
    exit 1
fi

echo "Flashing $IMAGE from sector 0..."
./sunxi-fel -p spiflash-write 0 "$IMAGE"

echo "Resetting device..."
./sunxi-fel wdreset

echo "Done! Full restore completed successfully."
echo "Device is rebooting..."
