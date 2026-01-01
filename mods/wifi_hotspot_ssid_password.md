# Custom WiFi Hotspot SSID and Password
Run adb shell and run these commands inside the shell, then reboot

```bash
setprop persist.sys.softap.ssid "MyCameraName"
setprop persist.sys.softap.pwd "12345678"
```