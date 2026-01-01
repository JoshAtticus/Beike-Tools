# Improved camera sensor configs
If your firmware does not have a folder with your sensor name in the /etc/hawkview folder, your images and videos will likely look like absolute dogshit.

Steal my configs from the configs folder, rename the folder to match your sensor, then edit sensor_list_cfg.ini to remove all other configs for other sensors, then add a config like this

```
sensor_name0            = "imx175" # change to your sensor name
... steal everything in between these 2 from the original thingy
isp_cfg_name0           = "imx175" # this should be the same as the folder name under /etc/hawkview
```

Once done, resquashfs and flash to mtdblock2