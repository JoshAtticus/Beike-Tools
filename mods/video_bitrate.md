# Video Bitrate
The stock firmware is dooky shart and records at 3mbps bitrate (💀)

You can unshittify it by editing /squashfs-root/etc/media_profiles.xml, set maxBitRate in VideoEncoderCap to 40000000, create a custom profile for 1080p with bitRate="32000000", you need a good U3/Class 10 SD Card (like Samsung Evo Plus)