
# WARNING
The development of nitroctl might slow down for a few months, the main reasons are that i have other things to do and that the screen of the Nitro 16 i use to test new features on failed. I will still try to keep adding new features but they will not be tested and may cause problems.

# Nitroctl, a CLI NitroSense alternative for Linux, Made thanks to the linuwu-sense driver.

## What is this?
A tool made with Python that lets you change keyboard RGB colors, thermal profiles, battery limiter and more using the Linuwu-Sense module. Currently, it works on Nitro devices only. Distro-agnostic, does not depend on systemd. Tested on Void Linux.

## Why did I make this?
[Another tool](https://github.com/PXDiv/Div-Acer-Manager-Max) that does the same thing wouldn't work on Void Linux so i decided to make my own, though mine lacks a GUI and is a bit less user friendly.

## Prerequisites

This tool depends on python and the [Linuwu-Sense](https://github.com/0x7375646F/Linuwu-Sense) module. The setup script should automatically install Linuwu-Sense and python on versions v1.2.26 and up.

## NOTICE ABOUT INSTALLATION

The GUI setup scripts (setup_kdialog.sh and setup_zenity.sh) require a running Polkit agent. If you dont have one and dont want to set one up, use the CLI script.

## INSTALLATION GUIDE IS PLANNED FOR A REWRITE, FOR THE MEANTIME USE THE MANUAL INSTALLATION METHOD (OR THE CLI SETUP SCRIPT)

## Manual installation

First, install Linuwu-Sense the same way its done above. Then, proceed with the installation as described below.

### Step 1: Install dependencies

The required dependencies are python3, python3-pip and git. Package names may be different on your distro. Below are the examples for Debian, Fedora, Arch and Void.

For Debian:

```bash
sudo apt install python3 python3-pip python-is-python3 git
```

For Fedora:

```bash
sudo dnf install python3 python3-pip git
```

For Arch:

```bash
sudo pacman -S python python-pip git
```

For Void:

```bash
sudo xbps-install -S python3 python3-pip git
```

### Step 2: Install nitroctl

Navigate to the destination you want to install nitroctl in your terminal. For example:

```bash
cd ~/your/destination/
```

Then, clone this repository:

```bash
git clone https://github.com/cani442k/nitroctl.git
```

cd into the cloned repository:

```bash
cd nitroctl
```

Make nitroctl.sh executable:

```bash
chmod +x nitroctl.sh
```

Run nitroctl:

```bash
./nitroctl.sh
```


## To Do

* [❌] Keyboard RGB
* [❌] GUI
* [❌] CPU&GPU Temparatures on main menu
* [✅] ~~Finish the installation guide~~
* [✅] ~~Configuration Save/Load function~~
