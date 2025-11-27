#!/usr/bin/python3

import os
import sys
import re
import subprocess
import argparse

VERBOSE = False


def true_size(s):
    u = {'B': 1, 'K': 1024, 'M': 1024*1024, 'G': 1024*1024*1024}
    if m := re.search(r'(\d+)([BKMG])', s):
        return int(m.group(1)) * u[m.group(2)]
    return 0


def nice_size(n):
    u = {'B': 1, 'K': 1024, 'M': 1024*1024, 'G': 1024*1024*1024}
    for k, v in reversed(u.items()):
        if n >= v and n % v == 0:
            return f"{n//v:,}{k}"
    return f"{n:,}B"


def check_exits(file):
    if not os.path.exists(file):
        print(f"FILE: {file} NOT FOUND!")
        exit(1)


def log(blk, image, blk_size):
    print(f"Flashed to {blk} with {nice_size(blk_size)} block.sz where {nice_size(os.path.getsize(image))} image.sz...")


def parse_part(part):
    if (m := re.search(r'(\d+[KMG])@(\d+[KMG])\((\w+)\)', part)) or (m := re.search(r'(\d+[KMG])\((\w+)\)', part)):
        if len(m.groups()) == 3:
            size = true_size(m.group(1))
            offset = true_size(m.group(2))
            image = m.group(3) + ".img"
            return image, size, offset
        else:
            size = true_size(m.group(1))
            image = m.group(2) + ".img"
            offset = 0
            return image, size, offset


def write_once(device, image_name):
    global_offset = 0
    blk_part = 1  # if more then one line with config

    check_exits(".env.txt")
    file_env = open(".env.txt")

    for line in file_env.readlines():
        if m := re.search(r'(blkdevparts|sd_parts)=(\w+)', line):
            mmcblk = m.group(2)

            partitions = re.sub(r'blkdevparts=\w+:', '', line).split(',')
            for part in partitions:
                image, size, offset = parse_part(part)

                if image_name == image:
                    check_exits(image)  # check if image exists in current directory
                    adb_dd(device, mmcblk+f"p{blk_part}", image)

                    log(mmcblk + f"p{blk_part}", image, size)
                    return

                global_offset += size
                blk_part += 1

    file_env.close()


def adb_dd(device, blk, image):
    print("Flashing partition in adb...")

    cmd = ["adb", "shell", f'dd if=/tmp/{image} of=/dev/{blk} bs=1k']
    if device != "":
        cmd = ["adb", "-s", str(device), "shell", f'dd if=/tmp/{image} of=/dev/{blk} bs=1k']
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        if VERBOSE:
            print(result.stdout, result.stderr)
    except Exception as e:
        print(f"ADB DD ERROR: {e}", e.stderr)
        sys.exit(0)


def adb_push(device, image):
    print("Pushing image to system...")

    cmd = ["adb", "push", str(image), "/"]
    if device != "":
        cmd = ["adb", "-s", str(device), "push", str(image), "/tmp/"]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        if VERBOSE:
            print(result.stdout, result.stderr)
    except Exception as e:
        print(f"ADB PUSH ERROR: {e}", e.stderr)
        sys.exit(0)


def adb_reboot(device):
    print("Rebooting the system...")

    cmd = ["adb", "shell", "reboot"]
    if device != "":
        cmd = ["adb", "-s", str(device), "shell", "reboot"]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
    except Exception as e:
        print(f"ADB REBOOT ERROR: {e}", e.stderr)
        sys.exit(0)


def main():
    global VERBOSE
    parser = argparse.ArgumentParser(description="Luckfox ADB OTA Updater")

    parser.add_argument('-d', "--device", metavar="DEV", help="ADB device id (ex: 9ad1s342)", default="")
    parser.add_argument('-i', "--image", metavar="IMG", help="Image (ex: boot.img)", required=True)
    parser.add_argument('-v', "--verbose", action="store_true", help="Print more verbose output")

    args = parser.parse_args()
    if args.verbose:
        VERBOSE = True

    adb_push(args.device, args.image)
    write_once(args.device, args.image)
    adb_reboot(args.device)


if __name__ == "__main__":
    main()
