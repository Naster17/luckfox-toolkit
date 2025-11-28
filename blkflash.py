#!/usr/bin/python3

import os
import sys
import re
import subprocess
import argparse


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


def dd(image, dev, offset):
    cmd = ['dd', f"if={image}", f"of={dev}", "bs=1k", f"seek={offset//1024}"]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        print(f"DD ERROR: {e}", e.stderr)
        sys.exit(0)


def check_exits(file):
    if not os.path.exists(file):
        print(f"FILE: {file} NOT FOUND!")
        exit(1)


def log(blk, image, blk_size, offset, global_offset):
    print(f"block...: {blk}")  # logical block
    print(f"image...: {image}")  # image aka boot.img rootfs.img etc
    print(f"image.sz: {nice_size(os.path.getsize(image))}")  # real image size
    print(f"block.sz: {nice_size(blk_size)}")  # reserved size for block
    print(f"used.sd.: {nice_size(global_offset + blk_size)}")  # used memory in sd (via reservation)
    if offset > 0:
        print(f"offset..: {nice_size(offset)}")  # custom offset if specified
    print()


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


def write_all(blk):
    global_offset = 0
    blk_part = 1  # if more then one line with config

    check_exits(".env.txt")
    file_env = open(".env.txt")

    for line in file_env.readlines():
        if m := re.search(r'(blkdevparts)=(\w+)', line):
            mmcblk = m.group(2)

            partitions = re.sub(r'blkdevparts=\w+:', '', line).split(',')
            for part in partitions:
                image, size, offset = parse_part(part)

                check_exits(image)  # check if image exists in current directory
                log(mmcblk + f"p{blk_part}", image, size, offset, global_offset)
                dd(image, blk, global_offset)  # write image using dd

                global_offset += size
                blk_part += 1

    file_env.close()


def write_once(blk, name):
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

                if name == image:
                    check_exits(image)  # check if image exists in current directory
                    log(mmcblk + f"p{blk_part}", image, size, offset, global_offset)
                    dd(image, blk, global_offset)  # write image using dd

                global_offset += size
                blk_part += 1

    file_env.close()


def main():
    parser = argparse.ArgumentParser(description="Luckfox SD Card Flasher")

    parser.add_argument('-d', "--device", metavar="DEV", help="Device path (ex: /dev/sdX)", required=True)
    parser.add_argument('-i', "--image", metavar="IMG", help="Write special image (ex: boot.img)")
    parser.add_argument('-c', "--confident", action="store_true", help="Disable warnings/alerts")

    args = parser.parse_args()
    if not args.confident:
        print(f"Writing to device: {args.device}")
        print("Disable alert: -c/--confident")
        input("[Press any Key]")
        print()

    if args.image:
        print(f"Writing {args.image} to {args.device}\n")
        write_once(args.device, args.image)
    else:
        print(f"Writing all to {args.device}\n")
        write_all(args.device)


if __name__ == "__main__":
    main()
