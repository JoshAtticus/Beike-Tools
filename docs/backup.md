# Backing up partitions
You WILL do this before flashing

```bash
adb pull /dev/block/mtdblock0
adb pull /dev/block/mtdblock1
adb pull /dev/block/mtdblock2
adb pull /dev/block/mtdblock3
adb pull /dev/block/mtdblock4
adb pull /dev/block/mtdblock5
adb pull /dev/block/mtdblock6
adb pull /dev/block/mtdblock7
```
You can then use make_full_restore in the scripts folder to turn the 7 partitions into one restore file, and flash the full restore file using flash_full_restore.

You can create a restore file manually using cat to combine all the partitions into 1 file, then to flash it use sunxi-fel to flash from offset 0.