# Memory Map & Flash Layout

The Allwinner V3 camera uses an SPI NOR Flash chip (usually 8MB). The system is divided into MTD (Memory Technology Device) blocks.

## Partition Table (Standard "Beike" Layout)

| Partition | Block Device | Content | Size (Approx) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Boot0** | `mtdblock0` | SPL / Bootloader | 256 KB | **DO NOT TOUCH**. Contains hardware init. |
| **Kernel** | `mtdblock1` | Linux Kernel / U-Boot | 2.5 MB | The OS core. |
| **System** | `mtdblock2` | **SquashFS RootFS** | ~4.7 MB | **Primary Modding Target**. Contains UI (`sdv`), configs, and drivers. |
| **Data** | `mtdblock3` | User Data | Variable | Writable partition (`/data`). Wifi configs, logs. |
| **Logo1** | `mtdblock4` | Boot Logo | 128 KB | Raw JPEG (220x176). |
| **Logo2** | `mtdblock5` | Shutdown Logo | 128 KB | Raw JPEG (220x176). |

## Flashing Offsets

When using `sunxi-fel` to flash specific partitions, you must write to the exact byte offset.

### The System Offset
To flash a modified **RootFS** (`system_vX.bin`) without bricking the bootloader:

**Offset Calculation:**
`Size(mtdblock0)` + `Size(mtdblock1)` = **Offset**

**For my specific device:**
*   mtdblock0: `262,144` bytes
*   mtdblock1: `2,621,440` bytes
*   **Target Offset:** **`2883584`**

### Command
> [!WARNING]
> 
> DO NOT FLASH IF YOUR NEW MODIFIED FILE IS LARGER THAN THE ORIGINAL, YOU WILL OVERWRITE OTHER PARTITIONS

```bash
./sunxi-fel -p spiflash-write 2883584 system_mod.bin
```
