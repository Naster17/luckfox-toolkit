#!/usr/bin/python3

import argparse
import sys
import struct
import zlib

CRC_SIZE = 4  # bytes


def str_to_int(s):
    try:
        return int(s, 0)
    except ValueError:
        print(f"Bad integer format: {s}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Make env.img from .env.txt")
    parser.add_argument('-s', type=str_to_int, help='Env size (def: 0x8000)', default=0x8000)  # aka 32kb
    parser.add_argument('-o', type=str, help='Output env.img (def: env.img)', default="env.img")
    parser.add_argument('-r', action='store_true', help='The environment has multiple copies in flash')
    parser.add_argument('-b', action='store_true', help='Set big endian (def: little endian)')
    parser.add_argument('-p', type=str_to_int, help='Fill the image with <byte> instead of 0xff', default=0x00)
    parser.add_argument('input_file', nargs='?', type=str, default=".env.txt", help='Env file (def: .env.txt)')

    args = parser.parse_args()

    datasize = args.s
    bin_filename = args.o
    redundant = args.r
    bigendian = args.b
    padbyte = args.p

    # Allocate space for the data
    dataptr = bytearray(datasize)
    envsize = datasize - (CRC_SIZE + (1 if redundant else 0))

    # Correct handling of environment pointer
    envptr = dataptr[CRC_SIZE + (1 if redundant else 0):]

    if args.input_file is None or args.input_file == "-":
        filebuf = sys.stdin.read()
    else:
        with open(args.input_file, 'r') as f:
            filebuf = f.read()

    if not filebuf:
        print("Error reading input file")
        sys.exit(1)

    # Parse input data
    lines = filebuf.splitlines()
    ep = 0

    # Initialize environment pointer with padding byte
    envptr[:] = [padbyte] * envsize

    for line in lines:
        if not line or line[0] == '#':
            continue  # Skip empty lines and comments

        encoded_line = line.encode() + b'\0'  # Add null terminator after each line
        if ep + len(encoded_line) > envsize:
            print("The environment file is too large for the target environment storage")
            sys.exit(1)

        envptr[ep:ep + len(encoded_line)] = encoded_line
        ep += len(encoded_line)
        print(f"Added variable: {line.strip()} at position {ep}")

    # Compute CRC
    crc = zlib.crc32(envptr) & 0xffffffff
    targetendian_crc = struct.pack('>I' if bigendian else '<I', crc)

    dataptr[:CRC_SIZE] = targetendian_crc
    dataptr[CRC_SIZE:] = envptr

    if redundant:
        dataptr[CRC_SIZE] = 1

    with open(bin_filename, 'wb') as bin_file:
        bin_file.write(dataptr)


if __name__ == "__main__":
    main()
