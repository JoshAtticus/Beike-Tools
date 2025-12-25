# Flashing
ready to die? cool, say hello to flashing. you WILL backup ALL partitions before you flash anything or I will hunt you down (in minecraft).

## entering fel/recovery mode
remove battery and sd card, hold volume up, insert cable, nothing will happen, an LED might turn on, that's fine.

## flashing
```bash
# flash
./sunxi-fel -p spiflash-write (offset) (image)

# restart
./sunxi-fel wdreset
```

## flashing a full restore
If you screwed up your partitions somehow, you can use the backup you absolutely 1000% created BEFORE flashing anything with the flash_full_restore tool in the scripts folder. Alternatively use sunxi-fel to flash the restore image from offset 0.

## will flashing brick my camera?
yes it can, that's why you make a backup, if you brick anything, you can flash all your partitions back to what they were before using allwinner fel mode.