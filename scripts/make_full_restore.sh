#!/usr/bin/env bash
set -euo pipefail

# Script to create a full restore image from mtdblock files

# Ask for version
read -r -p "Enter version (e.g. 1.0): " VERSION
if [[ -z "$VERSION" ]]; then
    echo "No version provided. Exiting."
    exit 1
fi

OUT="full_restore_v${VERSION}.bin"

# Check if mtdblock0 exists (required)
if [[ ! -f "mtdblock0" ]]; then
    echo "Error: mtdblock0 not found. This file is required."
    exit 1
fi

# Find consecutive mtdblock files starting from 0
declare -a blocks=()
blocks+=("mtdblock0")

# Check for mtdblock1-6 in order, stop at first missing
for i in {1..6}; do
    if [[ -f "mtdblock${i}" ]]; then
        blocks+=("mtdblock${i}")
    else
        # Stop at first missing block
        break
    fi
done

# Display what we found
echo "Found ${#blocks[@]} mtdblock file(s):"
for block in "${blocks[@]}"; do
    size=$(wc -c < "$block" | tr -d '[:space:]')
    printf "  %-12s %10s bytes\n" "$block" "$size"
done

# Calculate total size
total_size=0
for block in "${blocks[@]}"; do
    size=$(wc -c < "$block" | tr -d '[:space:]')
    total_size=$((total_size + size))
done

echo ""
echo "Total size: ${total_size} bytes"
read -r -p "Create $OUT? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborting."
    exit 1
fi

# Concatenate files
echo "Creating $OUT..."
cat "${blocks[@]}" > "$OUT"

# Verify size
out_size=$(wc -c < "$OUT" | tr -d '[:space:]')
if [[ "$out_size" -ne "$total_size" ]]; then
    echo "Error: Output size mismatch. Expected ${total_size}, got ${out_size}."
    rm -f "$OUT"
    exit 1
fi

echo "Success! Created $OUT (${out_size} bytes)"
echo "To flash this restore image, run: ./flash_full_restore.sh $OUT"
