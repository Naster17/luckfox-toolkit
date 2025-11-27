# luckfox-toolkit
Set of "quality of life" scripts and tools for luckfox developing

## Toolkit
```blkflash.py``` - Script for flashing to a block device using the default type **.env.txt**
```bash
./blkflash.py --device /dev/sdb # flash all in .env.txt
./blkflash.py -d /dev/sdb -i boot.img # flash special image to device
./blkfalsh.py --confident ... # disable alerts/warnings if you know what you do xD
```
