## 1. Microphone Fix
The default microphone gain is extremely low. The `sdv` binary uses `tinymix` (ALSA mixer) to set values on boot.

**Recommended Startup Script (`rcS`) additions:**
```bash
# Set ADC Gain to Max (63)
tinymix 1 63
# Set Mic Boost to Max (7) - ID 16 is specific to V3 codec
tinymix 16 7
```

## 2. "Speaker" Deshittifier
The speaker is a piezo buzzer (aka not a speaker). To prevent pain and suffering:

- Edit squashfs-root/etc/audio_policy.conf
- Reduce spk_gain max value from 60 to 40

## 3. Video Bitrate
The stock firmware is dooky shart and records at 3mbps bitrate (💀)

You can unshittify it by editing /squashfs-root/etc/media_profiles.xml, set maxBitRate in VideoEncoderCap to 40000000, create a custom profile for 1080p with bitRate="32000000", you need a good U3/Class 10 SD Card (like Samsung Evo Plus)

## 4. Hotspot Name & Password
Run adb shell and run these commands inside the shell, then reboot

```bash
setprop persist.sys.softap.ssid "MyCameraName"
setprop persist.sys.softap.pwd "12345678"
```

## 5. Sensor Configs
If your firmware does not have a folder with your sensor name in the /etc/hawkview folder, your images and videos will likely look like absolute dogshit.

Steal my configs from the configs folder, rename the folder to match your sensor, then edit sensor_list_cfg.ini to remove all other configs for other sensors, then add a config like this

```
sensor_name0            = "imx175" # change to your sensor name
... steal everything in between these 2 from the original thingy
isp_cfg_name0           = "imx175" # this should be the same as the folder name under /etc/hawkview
```

Once done, resquashfs and flash to mtdblock2