#!/usr/bin/env bash
set -euo pipefail

# Script to customize ROM settings before building

echo "ROM Customization Tool"
echo "====================="
echo ""

# Check if squashfs-root exists
if [[ ! -d "squashfs-root/res/cfg" ]]; then
    echo "Error: squashfs-root/res/cfg directory not found."
    echo "Run this script from the rom-building directory."
    exit 1
fi

CFG_DIR="squashfs-root/res/cfg"
MENU_CFG="${CFG_DIR}/menu.cfg"
CFG_220="${CFG_DIR}/220x176.cfg"
CFG_320="${CFG_DIR}/320x240.cfg"

# Function to update config value
update_config() {
    local file="$1"
    local key="$2"
    local value="$3"
    
    if [[ -f "$file" ]]; then
        sed -i.bak "s/^${key}=.*/${key}=${value}/" "$file"
        rm -f "${file}.bak"
    fi
}

echo "=== Firmware Information ==="
read -r -p "Product Type (e.g. Beike) [press Enter to skip]: " PRODUCT_TYPE
read -r -p "Manufacturer (e.g. JoshAtticus) [press Enter to skip]: " MANUFACTURER

if [[ -n "$PRODUCT_TYPE" || -n "$MANUFACTURER" ]]; then
    for cfg in "$CFG_220" "$CFG_320"; do
        if [[ -f "$cfg" ]]; then
            echo "  Updating $(basename "$cfg")"
            [[ -n "$PRODUCT_TYPE" ]] && update_config "$cfg" "product_type" "$PRODUCT_TYPE"
            [[ -n "$MANUFACTURER" ]] && update_config "$cfg" "Manufacturer" "$MANUFACTURER"
        fi
    done
fi

echo ""
echo "=== WiFi Settings ==="
read -r -p "WiFi SSID (e.g. Sports DV) [press Enter to skip]: " WIFI_SSID
read -r -p "WiFi Password (e.g. 12345678) [press Enter to skip]: " WIFI_PWD

if [[ -n "$WIFI_SSID" || -n "$WIFI_PWD" ]]; then
    for cfg in "$CFG_220" "$CFG_320"; do
        if [[ -f "$cfg" ]]; then
            echo "  Updating $(basename "$cfg")"
            [[ -n "$WIFI_SSID" ]] && update_config "$cfg" "wifi_ssid" "$WIFI_SSID"
            [[ -n "$WIFI_PWD" ]] && update_config "$cfg" "wifi_pwd" "$WIFI_PWD"
        fi
    done
fi

echo ""
echo "=== Menu Settings ==="
if [[ ! -f "$MENU_CFG" ]]; then
    echo "Warning: menu.cfg not found, skipping menu customization"
else
    echo ""
    echo "Language Options:"
    echo "  0=中文简体  1=中文繁体  2=English  3=日本語  4=한국어"
    echo "  5=Русский  6=Deutsch  7=Français  8=Italiano  9=Español"
    echo "  10=Polski  11=Nederlands  12=Português  13=ไทย  14=Čeština"
    echo "  15=Bahasa Indonesia  16=Türkçe"
    read -r -p "Language (0-16) [press Enter to skip]: " LANGUAGE
    
    echo ""
    echo "Video Resolution Options:"
    echo "  0=4K 30FPS  1=2.7K 30FPS  2=1080P 60FPS  3=1080P 30FPS"
    echo "  4=720P 120FPS  5=720P 60FPS  6=720P 30FPS"
    read -r -p "Video Resolution (0-6) [press Enter to skip]: " VIDEO_RES
    
    echo ""
    echo "Video Bitrate Options:"
    echo "  0=General  1=Good  2=Very Good  3=Wide (150°)"
    read -r -p "Video Bitrate (0-3) [press Enter to skip]: " VIDEO_BITRATE
    
    echo ""
    echo "Photo Resolution Options:"
    echo "  0=2M  1=5M  2=8M  3=12M  4=16M"
    read -r -p "Photo Resolution (0-4) [press Enter to skip]: " PHOTO_RES
    
    echo ""
    echo "Photo Quality Options:"
    echo "  0=General  1=Good  2=Very Good"
    read -r -p "Photo Quality (0-2) [press Enter to skip]: " PHOTO_QUALITY
    
    echo ""
    echo "G-Sensor Sensitivity Options:"
    echo "  0=Close  1=Low  2=Middle  3=High"
    read -r -p "G-Sensor (0-3) [press Enter to skip]: " GSENSOR
    
    echo ""
    echo "Screen Switch Options:"
    echo "  0=10s  1=20s  2=30s  3=Always On"
    read -r -p "Screen Switch (0-3) [press Enter to skip]: " SCREEN_SWITCH
    
    echo ""
    echo "Voice Volume Options:"
    echo "  0=High  1=Medium  2=Low  3=Off"
    read -r -p "Voice Volume (0-3) [press Enter to skip]: " VOICE_VOL
    
    echo ""
    echo "Light Frequency Options:"
    echo "  0=Auto  1=50Hz  2=60Hz"
    read -r -p "Light Frequency (0-2) [press Enter to skip]: " LIGHT_FREQ
    
    echo ""
    echo "Switch Settings (0=Off, 1=On):"
    read -r -p "Power On Record (0/1) [press Enter to skip]: " POWER_ON_RECORD
    read -r -p "Record Sound (0/1) [press Enter to skip]: " RECORD_SOUND
    read -r -p "Time Watermark (0/1) [press Enter to skip]: " TIME_WATERMARK
    read -r -p "Photo Watermark (0/1) [press Enter to skip]: " PHOTO_WATERMARK
    read -r -p "WiFi (0/1) [press Enter to skip]: " WIFI_SWITCH
    read -r -p "Key Tone (0/1) [press Enter to skip]: " KEYTONE
    read -r -p "LED Lights (0/1) [press Enter to skip]: " LED_LIGHTS
    
    echo ""
    echo "Updating menu.cfg..."
    
    [[ -n "$LANGUAGE" ]] && sed -i.bak "/^\[language\]/,/^current=/ s/^current=.*/current=${LANGUAGE}/" "$MENU_CFG"
    [[ -n "$VIDEO_RES" ]] && sed -i.bak "/^\[video_resolution\]/,/^current=/ s/^current=.*/current=${VIDEO_RES}/" "$MENU_CFG"
    [[ -n "$VIDEO_BITRATE" ]] && sed -i.bak "/^\[video_bitrate\]/,/^current=/ s/^current=.*/current=${VIDEO_BITRATE}/" "$MENU_CFG"
    [[ -n "$PHOTO_RES" ]] && sed -i.bak "/^\[photo_resolution\]/,/^current=/ s/^current=.*/current=${PHOTO_RES}/" "$MENU_CFG"
    [[ -n "$PHOTO_QUALITY" ]] && sed -i.bak "/^\[photo_compression_quality\]/,/^current=/ s/^current=.*/current=${PHOTO_QUALITY}/" "$MENU_CFG"
    [[ -n "$GSENSOR" ]] && sed -i.bak "/^\[gsensor\]/,/^current=/ s/^current=.*/current=${GSENSOR}/" "$MENU_CFG"
    [[ -n "$SCREEN_SWITCH" ]] && sed -i.bak "/^\[screen_switch\]/,/^current=/ s/^current=.*/current=${SCREEN_SWITCH}/" "$MENU_CFG"
    [[ -n "$VOICE_VOL" ]] && sed -i.bak "/^\[voicevol\]/,/^current=/ s/^current=.*/current=${VOICE_VOL}/" "$MENU_CFG"
    [[ -n "$LIGHT_FREQ" ]] && sed -i.bak "/^\[light_freq\]/,/^current=/ s/^current=.*/current=${LIGHT_FREQ}/" "$MENU_CFG"
    
    # Update switch settings
    [[ -n "$POWER_ON_RECORD" ]] && sed -i.bak "s/^power_on_record=.*/power_on_record=${POWER_ON_RECORD}/" "$MENU_CFG"
    [[ -n "$RECORD_SOUND" ]] && sed -i.bak "s/^record_sound=.*/record_sound=${RECORD_SOUND}/" "$MENU_CFG"
    [[ -n "$TIME_WATERMARK" ]] && sed -i.bak "s/^time_water_mark=.*/time_water_mark=${TIME_WATERMARK}/" "$MENU_CFG"
    [[ -n "$PHOTO_WATERMARK" ]] && sed -i.bak "s/^photo_water_mark=.*/photo_water_mark=${PHOTO_WATERMARK}/" "$MENU_CFG"
    [[ -n "$WIFI_SWITCH" ]] && sed -i.bak "s/^wifi=.*/wifi=${WIFI_SWITCH}/" "$MENU_CFG"
    [[ -n "$KEYTONE" ]] && sed -i.bak "s/^keytone=.*/keytone=${KEYTONE}/" "$MENU_CFG"
    [[ -n "$LED_LIGHTS" ]] && sed -i.bak "s/^LED_lights = .*/LED_lights = ${LED_LIGHTS}/" "$MENU_CFG"
    
    rm -f "${MENU_CFG}.bak"
fi

echo ""
echo "=== Debloating ==="
read -r -p "Enable debloating (exclude files from build)? (y/N): " DEBLOAT

if [[ "$DEBLOAT" =~ ^[Yy]$ ]]; then
    echo "Configuring debloat options..."
    
    # Create .mksquashfs_exclude file
    EXCLUDE_FILE=".mksquashfs_exclude"
    > "$EXCLUDE_FILE"  # Clear/create file
    
    # Disable fake features in menu.cfg
    if [[ -f "$MENU_CFG" ]]; then
        sed -i.bak "/^\[gsensor\]/,/^count=/ s/^count=.*/count=0/" "$MENU_CFG"
        sed -i.bak "/^\[park_mode\]/,/^count=/ s/^count=.*/count=0/" "$MENU_CFG"
        rm -f "${MENU_CFG}.bak"
        echo "  ✓ Disabled gsensor and park_mode in menu"
    fi
    
    # Add unused drivers to exclude list
    if [[ -d "squashfs-root/vendor/modules" ]]; then
        driver_count=0
        while IFS= read -r -d '' file; do
            # Convert to path relative to squashfs-root
            rel_path="${file#squashfs-root/}"
            echo "$rel_path" >> "$EXCLUDE_FILE"
            ((driver_count++))
        done < <(find squashfs-root/vendor/modules -name "mma*" -o -name "bma*" -print0)
        
        if [[ $driver_count -gt 0 ]]; then
            echo "  ✓ Added ${driver_count} unused drivers to exclude list"
        fi
    fi
    
    # Process user's exclude.txt if it exists
    if [[ -f "exclude.txt" ]]; then
        echo "Processing exclude.txt..."
        excluded_count=0
        
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Skip empty lines and comments
            [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
            
            # Remove leading/trailing whitespace
            line=$(echo "$line" | xargs)
            
            # Convert to path relative to squashfs-root
            if [[ "$line" == squashfs-root/* ]]; then
                rel_path="${line#squashfs-root/}"
            else
                rel_path="$line"
            fi
            
            # Check if path exists
            full_path="squashfs-root/$rel_path"
            if [[ -e "$full_path" ]]; then
                echo "$rel_path" >> "$EXCLUDE_FILE"
                echo "  ✓ Will exclude: $rel_path"
                ((excluded_count++))
            else
                echo "  ⚠ Not found (skipping): $rel_path"
            fi
        done < exclude.txt
        
        if [[ $excluded_count -gt 0 ]]; then
            echo "  ✓ Added ${excluded_count} items from exclude.txt"
        fi
    fi
    
    echo "  ✓ Debloat configuration saved to $EXCLUDE_FILE"
    echo "    This will be used during the next build."
else
    # Remove exclude file if debloating is disabled
    if [[ -f ".mksquashfs_exclude" ]]; then
        rm -f ".mksquashfs_exclude"
        echo "  ✓ Debloating disabled - removed exclude file"
    fi
fi

echo ""
echo "✓ Customization complete!"
echo ""
echo "To build the ROM with these settings, run: ./build.sh"
