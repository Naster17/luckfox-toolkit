# luckfox-toolkit
#### I'm open to suggestions for what other tools to add

## Toolkit
```blkflash.py``` - Flashing to a block device using the default type **.env.txt**
```bash
./blkflash.py --device /dev/sdb # flash all in .env.txt
./blkflash.py -d /dev/sdb -i boot.img # flash special image to device
./blkfalsh.py --confident ... # disable alerts/warnings if you know what you do xD
```
```adbota.py``` - Perform OTA updates via ADB (keep **.env.txt** in same dir)  
```bash
./adbota.py -i boot.img # update boot
./adbota.py -d 9f5teda -i env.img # if more then one device connected use --device
./adbota.py -v -i boot.img # verbose output
```
```mkenv.py``` - Making env.img from **.env.txt** (ex: for partitions etc)  
```bash
# if you resize the middle partitions like boot, oem, you have to rewrite everything to the SD card with blkflash NO OTA
./mkenv.py # automaticaly owerwrite env.img using .env.txt in current dir
./mkenv.py -s 0x8000 -p 0x0 -o env.img .env.txt # 32kb img size with 0x00 fill
./mkenv.py -o env_new.img # write in new .img
```
```modinstall.py``` - Install kernel modules to system from **INSTALL_MOD_PATH**
```bash
# when build kernel: make -j$(nproc) INSTALL_MOD_PATH=/path/to/output/ modules_install
./modinstall.py -p /path/to/output/ # upload all kernel modules from install path
./modinstall.py -d 9f5teda -p /path/to/output/ # to specific device
# now you can fully modprope ex: modprope rknpu 
```
