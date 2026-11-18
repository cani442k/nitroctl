#!/usr/bin/env python3
import sys
import shutil
import os
import subprocess
import time
from pathlib import Path
from cls import cls
def batLimit():
    cls()
    current_battery_limit_state = Path("/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/battery_limiter").read_text().strip()
    print("Do you want to enable or disable battery limiter?")
    if current_battery_limit_state == "1":
        print("Current state is: Enabled\n")
    elif current_battery_limit_state == "0":
        print("Current state is: Disabled\n")
    else:
        print("Current state unknown\n")
    print("1: Enable")
    print("2: Disable")
    battery_limit_state = input("Type the number of your choice, then press enter.\n").strip()
    if battery_limit_state == "1":
        subprocess.run("echo 1 | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/battery_limiter", shell=True)
    elif battery_limit_state == "2":
        subprocess.run("echo 0 | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/battery_limiter", shell=True)
    else:
        print("Unknown state. Returning to main menu.")
        time.sleep(1)
