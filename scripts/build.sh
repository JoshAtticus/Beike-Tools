#!/usr/bin/env bash
set -euo pipefail

# Ask for build information
read -r -p "Enter version (e.g. 1.0): " VERSION
if [[ -z "$VERSION" ]]; then
    echo "No version provided. Exiting."
    exit 1
fi

read -r -p "Enter build number (e.g. 8): " BUILD_NUM
if [[ -z "$BUILD_NUM" ]]; then
    echo "No build number provided. Exiting."
    exit 1
fi

read -r -p "Enter product type (e.g. Beike): " PRODUCT_TYPE
if [[ -z "$PRODUCT_TYPE" ]]; then
    echo "No product type provided. Exiting."
    exit 1
fi

read -r -p "Enter manufacturer (e.g. JoshAtticus): " MANUFACTURER
if [[ -z "$MANUFACTURER" ]]; then
    echo "No manufacturer provided. Exiting."
    exit 1
fi

# Ask about experimental compression
read -r -p "Use experimental extra compression? (yes/if needed/no): " USE_EXPERIMENTAL
USE_EXPERIMENTAL=$(echo "$USE_EXPERIMENTAL" | tr '[:upper:]' '[:lower:]')

# Get current date in YYYYMMDD format
CURRENT_DATE=$(date +%Y%m%d)

OUT="system_v${VERSION}.bin"

# Preconditions
if ! command -v mksquashfs >/dev/null 2>&1; then
    echo "mksquashfs not found in PATH. Install squashfs-tools."
    exit 1
fi
if [[ ! -d "squashfs-root" ]]; then
    echo "Directory 'squashfs-root' not found in $(pwd)."
    exit 1
fi
if [[ ! -d "sunxi-tools" ]]; then
    echo "Directory 'sunxi-tools' not found in $(pwd)."
    exit 1
fi

# Update firmware information in config files
echo "Updating firmware information..."
SOFTWARE_VERSION="${BUILD_NUM}"

for cfg_file in squashfs-root/res/cfg/220x176.cfg squashfs-root/res/cfg/320x240.cfg; do
    if [[ -f "$cfg_file" ]]; then
        echo "  Updating $cfg_file"
        # Use sed to update the firmware_information section
        sed -i.bak "s/^product_type=.*/product_type=${PRODUCT_TYPE}/" "$cfg_file"
        sed -i.bak "s/^software_version=.*/software_version=${SOFTWARE_VERSION}/" "$cfg_file"
        sed -i.bak "s/^updated=.*/updated=${CURRENT_DATE}/" "$cfg_file"
        sed -i.bak "s/^Manufacturer=.*/Manufacturer=${MANUFACTURER}/" "$cfg_file"
        sed -i.bak "s/^date_number=.*/date_number=${CURRENT_DATE}/" "$cfg_file"
        rm -f "${cfg_file}.bak"
    else
        echo "  Warning: $cfg_file not found, skipping"
    fi
done

# Create squashfs image
echo "Creating $OUT from squashfs-root..."

# Check for debloat exclude file
EXCLUDE_OPTS=""
if [[ -f ".mksquashfs_exclude" ]]; then
    echo "Using debloat exclusions from .mksquashfs_exclude"
    EXCLUDE_OPTS="-ef .mksquashfs_exclude"
fi

# Determine compression method
if [[ "$USE_EXPERIMENTAL" == "yes" ]]; then
    echo "Using experimental extra compression..."
    mksquashfs squashfs-root "$OUT" -comp xz -Xbcj arm -b 1M -no-xattrs $EXCLUDE_OPTS
else
    # Build with standard compression
    mksquashfs squashfs-root "$OUT" -comp xz -no-xattrs $EXCLUDE_OPTS
fi

# Verify size against mtdblock2
if [[ ! -f "mtdblock2" ]]; then
    echo "Warning: mtdblock2 not found. Cannot verify size."
else
    out_size=$(wc -c < "$OUT" | tr -d '[:space:]')
    mtd_size=$(wc -c < "mtdblock2" | tr -d '[:space:]')
    
    if (( out_size >= mtd_size )); then
        if [[ "$USE_EXPERIMENTAL" == "if needed" ]]; then
            echo "Image too large: ${out_size} bytes >= ${mtd_size} bytes"
            echo "Retrying with experimental extra compression..."
            rm -f "$OUT"
            mksquashfs squashfs-root "$OUT" -comp xz -Xbcj arm -b 1M -no-xattrs $EXCLUDE_OPTS
            
            # Check size again
            out_size=$(wc -c < "$OUT" | tr -d '[:space:]')
            if (( out_size >= mtd_size )); then
                echo "Error: Even with extra compression, image is too large: ${out_size} bytes >= ${mtd_size} bytes"
                exit 1
            fi
            echo "Success with extra compression: ${out_size} bytes < ${mtd_size} bytes"
        else
            echo "Error: Generated image ($OUT) is too large: ${out_size} bytes >= mtdblock2 (${mtd_size} bytes)."
            if [[ "$USE_EXPERIMENTAL" == "no" ]]; then
                echo "Try again with experimental compression (answer 'yes' or 'if needed' when prompted)."
            fi
            exit 1
        fi
    else
        echo "Size check passed: ${out_size} bytes < ${mtd_size} bytes"
    fi
fi

# Copy into sunxi-tools for flashing
cp -f "$OUT" sunxi-tools/

echo "Build complete: $OUT"
echo "To flash to device, run: ./flash.sh $OUT"