#!/usr/bin/env python3
import sys
import shutil
import os
import subprocess
import time
from pathlib import Path

sudo_user = os.environ.get("SUDO_USER")
real_home = Path(f"/home/{sudo_user}") if sudo_user else Path.home()
configs_dir = real_home / ".config" / "nitroctl"
def savecfg():
    configs_dir.mkdir(parents=True, exist_ok=True)
    sysfs_path = Path("/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense")
    for item in sysfs_path.iterdir():
        if item.is_file():
            try:
                content = item.read_text().strip()
                
                dest_file = configs_dir / item.name
                dest_file.write_text(content)
                
                print(f"Copied {item.name} to {dest_file}")
            except Exception as e:
                print(f"Skipped {item.name}: {e}")
    

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
    print("4: Fan Speed")
    print("5: LCD Overdrive")
    print("6: Keyboard RGB Configuration")
    print("S: Save current configuration")
    print("L: Load configuration from default path")
    print("Q: Quit program")
    return input("Type the number of your choice, then press enter.\n").strip()
while True:
    next_function = mainloop()

    if next_function.lower() == "q":
        cls()
        print("Exiting. Goodbye!")
        break
        sys.exit(0)
    elif next_function.lower() == "s":
        print("Saving configuration to default directory: ~/.config/nitroctl")
        savecfg()
        time.sleep(1)
        continue
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
            time.sleep(1)
    elif next_function == "3":
        cls()
        current_battery_limit_state = Path("/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/battery_limiter").read_text().strip()
        print("Do you want to enable or disable battery limiter?")
        if current_battery_limit_state == "1":
            print("Current state is: Enabled")
        elif current_battery_limit_state == "0":
            print("Current state is: Disabled")
        else:
            print("Current state unknown")
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
    elif next_function == "4":
        cls()
        print("Fan speed control")
        print("Do you want manual or automatic CPU fan control?")
        print("1: Automatic")
        print("2: Manual")
        cpu_automation = input("Type the number of your choice, then press enter.\n").strip()
        if cpu_automation == "1":
            print("Automatic CPU fan control selected.\n")
            cpu_speed = 0
        elif cpu_automation not in ("1", "2"):
            print("Unknown state. Returning to main menu.")
            time.sleep(1)
            continue
        elif cpu_automation == "2":
            VALID_SPEEDS = {str(i) for i in range(1, 101)}
            cpu_speed = input("Manual CPU fan control selected. Type your desired fan speed. (valid range: 1-100, 1 being the lowest and 100 being max.)\n ").strip()
            if cpu_speed not in VALID_SPEEDS:
                print("Invalid input. Please enter a number between 1 and 100. Returning to main menu.\n")
                time.sleep(1)
                continue
                
        print("Do you want manual or automatic GPU fan control?")
        print("1: Automatic")
        print("2: Manual")
        
        gpu_automation = input("Type the number of your choice, then press enter.\n").strip()
        if gpu_automation == "1":
            print("Automatic GPU fan control selected.\n")
            gpu_speed = 0
        elif gpu_automation not in ("1", "2"):
            print("Unknown state. Returning to main menu.")
            time.sleep(1)
            continue
        elif gpu_automation == "2":
            gpu_speed = input("Manual GPU fan control selected. Type your desired fan speed. (valid range: 1-100, 1 being the lowest and 100 being max.)\n ").strip()
            if gpu_speed not in VALID_SPEEDS:
                print("Invalid input. Please enter a number between 1 and 100. Returning to main menu.\n")
                time.sleep(1)
                continue
        
        print("Target speeds are:")
        print(f"CPU Speed: {cpu_speed}")
        print(f"GPU Speed: {gpu_speed}")
        areyousurethesespeedsarecorrect = input("Is this correct? y/n").strip().lower()
        if areyousurethesespeedsarecorrect == "y":
            subprocess.run(f"echo {cpu_speed},{gpu_speed} | sudo tee /sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense/fan_speed", shell=True)
        else:
            print("Returning to main menu.")
            time.sleep(1)
            continue
        
        
        
    
