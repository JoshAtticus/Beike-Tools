# Interesting Findings

## The camera sensor is faked
On my camera, the sensor info is quite hard to find. The firmware is clearly based on the firmware for an IMX179/179S sensor, however mine actually has an IMX175. The build number indicates it has an IMX179, the camera configs indicates it has an IMX179S, but the only camera driver is for the IMX175.

## Also for dashcams?
I ran strings on the sdv binary, which controls the entire UI, and found many strings for things you'd usually only find on dashcams, like parking sensors, and collision detection. It also features support for gyro sensors (presumably for collision detection and possibly EIS,) however as far as I can tell, none of the cheap Allwinner V3/V3S action cameras online have gyro sensors.

## Built in SD Card speed test (not really)
As far as I can tell from the language file, there is supposed to be an SD card speed test, although these strings aren't actually used anywhere in the sdv binary, at least on my firmware.

## Leftovers from an Android Emulator build
I don't really know what I expected from a hodge-podge incredibly stripped down Android 4.2.2 build that literally doesn't even have Android Framework itself, but I did not expect leftovers from the Android Emulator of all things. in /etc, there's an init.goldfish.sh file, a leftover from the old android virtual device emulator. It doesn't actually get executed though.

## Deleting the Chinese or English language packs breaks the XDV app
I mean the title kind of told you everything, but yeah the XDV phone app explodes if it can't download those files from the camera.