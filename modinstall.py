#!/usr/bin/python3

import os
import sys
import re
import subprocess
import argparse

VERBOSE = False


def check_exits(file):
    if not os.path.exists(file):
        print(f"FILE: {file} NOT FOUND!")
        exit(1)


def adb_exec(device, command):
    cmd = ["adb"] + command
    if device != "":
        cmd = ["adb", "-s", str(device)] + command
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        if VERBOSE:
            print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("ADB ERROR:")
        print("CMD:", " ".join(cmd))
        print(e.stdout, e.stderr)
        sys.exit(1)


def install_bare(device, path):
    try:
        folder_path = os.path.normpath(path)

        for root, dirs, files in os.walk(path):
            relative_path = os.path.relpath(root, folder_path)
            depth = relative_path.count(os.sep)

            if depth >= 2:
                print(f"mkdir: {os.path.join('/', relative_path)}")
                adb_exec(device, ["shell", "mkdir", "-p", os.path.join('/', relative_path)])

                for dir_name in dirs:
                    print(f"mkdir: {os.path.join('/', relative_path, dir_name)}")
                    adb_exec(device, ["shell", "mkdir", "-p", os.path.join('/', relative_path, dir_name)])

                for file_name in files:
                    if file_name in ["source", "build"]:
                        continue

                    _path = os.path.join('/', relative_path, file_name)
                    print(f"push.: {_path}")
                    adb_exec(device, ["push", path + _path, os.path.dirname(_path)])

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    global VERBOSE
    parser = argparse.ArgumentParser(description="Luckfox ADB OTA Updater")

    parser.add_argument('-d', "--device", metavar="DEV", help="ADB device id (ex: 9ad1s342)", default="")
    parser.add_argument('-p', "--path", metavar="PATH", help="Path to INSTALL_MOD_PATH folder", required=True)
    parser.add_argument('-v', "--verbose", action="store_true", help="Print more verbose output")

    args = parser.parse_args()
    if args.verbose:
        VERBOSE = True

    if "root" not in adb_exec(args.device, ["shell", "id"]):
        print("require root privalege on adb")
        exit(1)

    install_bare(args.device, args.path)
    print("Finised...")


if __name__ == "__main__":
    main()
