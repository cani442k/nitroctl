#!/usr/bin/env python3
import sys
import subprocess
import time

import nitro_core as core


def cls():
    subprocess.run(["clear"])


def explain(exc: Exception) -> str:
    if isinstance(exc, PermissionError):
        return "Permission denied. Run nitroctl as root (sudo)."
    return str(exc)


def chk_os():
    if not core.is_linux():
        print(f"ERROR: Fatal: detected OS: {sys.platform}! nitroctl is built exclusively for Linux and will not function on any other OS. Exiting.", file=sys.stderr)
        sys.exit(1)


def chk_su():
    if not core.is_root():
        print("ERROR: Fatal: nitroctl requires root privileges. Exiting.", file=sys.stderr)
        sys.exit(1)


def chk_driver():
    base = core.driver_base()
    if base is None:
        print(f"ERROR: Fatal: Driver directory '{core.SENSE_BASES[0]}' does not exist! Device might not be Acer. Exiting.", file=sys.stderr)
        sys.exit(1)
    if not core.features():
        print("ERROR: Fatal: nitro_sense directory not found in linuwu_sense directory. linuwu_sense might not be properly installed. Exiting.", file=sys.stderr)
        sys.exit(1)


def report(result, verb):
    done, skipped = result
    for name in done:
        print(f"{verb} {name}")
    for name, reason in skipped:
        print(f"Skipped {name}: {reason}")


def thermal_profile_menu():
    cls()
    try:
        profiles = core.thermal_profiles()
    except OSError as exc:
        print(f"ERROR: Could not read available thermal modes: {exc}")
        time.sleep(2)
        return
    current = core.current_thermal_profile()

    print("Available thermal modes:")
    for idx, (mode, label) in enumerate(profiles, start=1):
        marker = " (current)" if mode == current else ""
        print(f"{idx}: {label}{marker}")

    thermal_profile = input("Type the number of the mode you want to apply, then press enter.\n").strip()

    if thermal_profile.isdigit():
        idx = int(thermal_profile) - 1
        if 0 <= idx < len(profiles):
            try:
                core.set_thermal_profile(profiles[idx][0])
                print(f"Thermal mode set to {profiles[idx][1]}.")
            except OSError as exc:
                print(f"ERROR: {explain(exc)}")
            time.sleep(1)
        else:
            print("Invalid selection. Returning to main menu.")
            time.sleep(1)


def toggle_menu(attr, title, on_label="Enabled", off_label="Disabled"):
    """Menu de liga/desliga compartilhado por RGB timeout, bateria e LCD."""
    cls()
    if not core.supports(attr):
        print(f"ERROR: This device does not expose '{attr}'. Feature unavailable.")
        time.sleep(2)
        return
    print(f"Do you want to enable or disable {title}?")
    state = core.read_flag(attr)
    if state is True:
        print(f"Current state is: {on_label}\n")
    elif state is False:
        print(f"Current state is: {off_label}\n")
    else:
        print("Current state unknown.\n")
    print(f"1: {on_label}")
    print(f"2: {off_label}")
    choice = input("Type the number of your choice, then press enter.\n").strip()
    if choice in ("1", "2"):
        try:
            core.set_flag(attr, choice == "1")
            print(f"{title} {'enabled' if choice == '1' else 'disabled'}.")
        except OSError as exc:
            print(f"ERROR: {explain(exc)}")
        time.sleep(1)
    else:
        print("Unknown state. Returning to main menu.")
        time.sleep(1)


def ask_fan_speed(device):
    print(f"Do you want manual or automatic {device} fan control?")
    print("1: Automatic")
    print("2: Manual")
    choice = input("Type the number of your choice, then press enter.\n").strip()
    if choice == "1":
        print(f"Automatic {device} fan control selected.\n")
        return core.FAN_AUTO
    if choice != "2":
        print("Unknown state. Returning to main menu.")
        time.sleep(1)
        return None
    speed = input(
        f"Manual {device} fan control selected. Type your desired fan speed. "
        f"(valid range: {core.FAN_MIN}-{core.FAN_MAX}, {core.FAN_MIN} being the lowest and {core.FAN_MAX} being max.)\n "
    ).strip()
    if not core.valid_fan_speed(speed) or int(speed) == core.FAN_AUTO:
        print(f"Invalid input. Please enter a number between {core.FAN_MIN} and {core.FAN_MAX}. Returning to main menu.\n")
        time.sleep(1)
        return None
    return int(speed)


def fan_speed_menu():
    cls()
    if not core.supports("fan_speed"):
        print("ERROR: This device does not expose 'fan_speed'. Feature unavailable.")
        time.sleep(2)
        return
    print("Fan speed control")
    cpu_speed = ask_fan_speed("CPU")
    if cpu_speed is None:
        return
    gpu_speed = ask_fan_speed("GPU")
    if gpu_speed is None:
        return

    print("Target speeds are:")
    print(f"CPU Speed: {cpu_speed}")
    print(f"GPU Speed: {gpu_speed}")
    confirm = input("Is this correct? y/n").strip().lower()
    if confirm != "y":
        print("Returning to main menu.")
        time.sleep(1)
        return
    try:
        core.set_fan_speed(cpu_speed, gpu_speed)
        print("Fan speeds applied.")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {explain(exc)}")
    time.sleep(1)


def mainloop():
    cls()
    print("Welcome to nitroctl!")
    print("Choose one of the following to continue:")
    print("1: Thermal Profile")
    print("2: Keyboard RGB Timeout")
    print("3: Battery Limiter")
    print("4: Fan Speed")
    print("5: LCD Overdrive")
    print("6: Keyboard RGB Configuration [UNIMPLEMENTED]")
    print("S: Save current configuration")
    print("L: Load configuration from default path [UNTESTED, MIGHT BREAK YOUR SYSTEM!]")
    print("Q: Quit program")
    return input("Type the number of your choice, then press enter.\n").strip()


def run():
    chk_os()
    chk_su()
    chk_driver()

    while True:
        next_function = mainloop()
        choice = next_function.lower()

        if choice == "q":
            cls()
            print("Exiting. Goodbye!")
            break
        elif choice == "s":
            print("Saving configuration to default directory: ~/.config/nitroctl")
            try:
                report(core.save_config(), "Copied")
            except OSError as exc:
                print(f"ERROR: {explain(exc)}")
            time.sleep(1)
        elif next_function == "1":
            thermal_profile_menu()
        elif next_function == "2":
            toggle_menu("backlight_timeout", "keyboard RGB timeout")
        elif next_function == "3":
            toggle_menu("battery_limiter", "battery limiter")
        elif next_function == "4":
            fan_speed_menu()
        elif next_function == "5":
            toggle_menu("lcd_override", "LCD Overdrive")
        elif next_function == "6":
            cls()
            print("Keyboard RGB configuration is not implemented by the nitroctl project yet.")
            time.sleep(2)
        elif choice == "l":
            print(f"Loading previous configuration from {core.config_dir()}")
            try:
                report(core.load_config(), "Loaded")
                print("Loading finished.")
            except OSError as exc:
                print(f"ERROR: {explain(exc)}")
            time.sleep(1)
        else:
            print("Unknown option. Returning to main menu.")
            time.sleep(1)


if __name__ == "__main__":
    run()