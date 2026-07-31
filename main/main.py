#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

def cls():
	subprocess.run(["clear"])

def chk_os():
	if not sys.platform.startswith("linux"):
		print(f"ERROR: Fatal: detected OS: {sys.platform}! nitroctl is built exclusively for Linux and will not function on any other OS. Exiting.", file=sys.stderr)
		sys.exit(1)
def chk_su():
	if os.geteuid() != 0:
		print("ERROR: Fatal: nitroctl requires root privileges. Exiting.", file=sys.stderr)
		sys.exit(1)

linuwusense_dir = "/sys/devices/platform/acer-wmi"

if not os.path.exists(linuwusense_dir):
    print(f"ERROR: Fatal: Driver directory '{linuwusense_dir}' does not exist! Exiting.", file=sys.stderr)
    sys.exit(1)

if os.path.exists(linuwusense_dir):
    subdirs_of_linuwusense = [entry.name for entry in os.scandir(linuwusense_dir) if entry.is_dir()]
if not "nitro_sense" in subdirs_of_linuwusense:
	print("ERROR: Fatal: nitro_sense directory not found in linuwu_sense directory. linuwu_sense might not be properly installed. Exiting.", file=sys.stderr)
	sys.exit(1)
chk_os()
chk_su()
def mainloop():	
	cls()
	print("Welcome to nitroctl!")
	print("Choose one of the following to continue:")
	print("1: Thermal Profile")
	print("2: Keyboard RGB Timeout")
	print("3: Battery Limiter")
	print("4: Fan Speed #not implemented yet")
	print("5: LCD Overdrive")
	print("6: Keyboard RGB Configuration")
	print("Q: Quit program")
	return input("Type the number of your choice, then press enter.\n").strip()
while True:
    next_function = mainloop()

    if next_function.lower() == "q":
        cls()
        print("Exiting. Goodbye!")
        break
        sys.exit(0)
    elif next_function == "1":
        raw_modes = Path("/sys/firmware/acpi/platform_profile_choices").read_text().split()
        LABEL_MAP = {
            "balanced-performance": "Performance",
            "performance": "Turbo",
            "low-power": "Eco",
            "balanced": "Balanced",
            "quiet": "Quiet",
        }
        display_modes = [LABEL_MAP.get(mode, mode) for mode in raw_modes]
        
        cls()
        print("Available thermal modes:")
        for idx, mode in enumerate(display_modes, start=1):
            print(f"{idx}: {mode}")
        
        thermal_profile = input("Type the number of the mode you want to apply, then press enter.\n").strip()
        
        if thermal_profile.isdigit():
            idx = int(thermal_profile) - 1
            if 0 <= idx < len(raw_modes):
                chosen_mode = raw_modes[idx]
                subprocess.run(f"echo {chosen_mode} | sudo tee /sys/firmware/acpi/platform_profile", shell=True)
    elif next_function == "2":
        cls()
        print("Do you want to enable or disable keyboard RGB timeout?")
        current_rgb_state = Path("/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/backlight_timeout").read_text().strip()
        if current_rgb_state == "1":
            print("Current state is: Enabled")
        elif current_rgb_state == "0":
            print("Current state is: Disabled")
        else:
            print("Current state unknown.")
        print("1: Enable")
        print("2: Disable")
        rgb_state = input("Type the number of your choice, then press enter.\n").strip()
        if rgb_state == "1":
            subprocess.run("echo 1 | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/backlight_timeout", shell=True)
        elif rgb_state == "0":
            subprocess.run("echo 0 | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/backlight_timeout", shell=True)
        else:
            print("Unknown state. Returning to main menu.")
            
            
            
        
        
        
    
