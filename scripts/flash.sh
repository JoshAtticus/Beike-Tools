#!/usr/bin/env bash
set -euo pipefail

# Script to flash system image to device using sunxi-fel

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
    # List available system_v*.bin files
    shopt -s nullglob
    images=(system_v*.bin)
    shopt -u nullglob
    
    if [[ ${#images[@]} -eq 0 ]]; then
        echo "No system_v*.bin files found in $(pwd)."
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

# Verify size against mtdblock2
if [[ ! -f "../mtdblock2" ]]; then
    echo "Warning: mtdblock2 not found. Cannot verify size."
    read -r -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    img_size=$(wc -c < "$IMAGE" | tr -d '[:space:]')
    mtd_size=$(wc -c < "../mtdblock2" | tr -d '[:space:]')
    
    if (( img_size >= mtd_size )); then
        echo "Error: Image ($IMAGE) is too large: ${img_size} bytes >= mtdblock2 (${mtd_size} bytes)."
        exit 1
    fi
    echo "Size check passed: ${img_size} bytes < ${mtd_size} bytes"
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

# Flash using sunxi-fel
if [[ ! -x "./sunxi-fel" ]]; then
    echo "./sunxi-fel not found or not executable in $(pwd)."
    exit 1
fi

echo "Flashing $IMAGE..."
./sunxi-fel -p spiflash-write 2883584 "$IMAGE"

echo "Resetting device..."
./sunxi-fel wdreset

echo "Done! Device flashed successfully."
