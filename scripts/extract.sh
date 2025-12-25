#!/usr/bin/env bash
set -euo pipefail

# Script to extract mtdblock2 into squashfs-root

# Check for unsquashfs command
if ! command -v unsquashfs >/dev/null 2>&1; then
    echo "unsquashfs not found in PATH. Install squashfs-tools."
    exit 1
fi

# Determine mtdblock2 location
if [[ -f "mtdblock2" ]]; then
    MTDBLOCK="mtdblock2"
elif [[ -f "../mtdblock2" ]]; then
    MTDBLOCK="../mtdblock2"
else
    echo "mtdblock2 not found in current directory or parent directory."
    exit 1
fi

echo "Found mtdblock2: $MTDBLOCK"

# Check if squashfs-root exists
if [[ -d "squashfs-root" ]]; then
    echo "Warning: squashfs-root directory already exists."
    read -r -p "Delete and re-extract? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        rm -rf squashfs-root
    else
        echo "Aborting."
        exit 1
    fi
fi

# Extract
echo "Extracting $MTDBLOCK..."
unsquashfs "$MTDBLOCK"

echo "Done! Extracted to squashfs-root/"
