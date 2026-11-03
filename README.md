
# LOOKING FOR BETA TESTERS
I have sold my Acer Nitro laptop. I will add some final patches to nitroctl, then archive the repository for good if i cannot find anyone to do beta testing. I will be working on a GUI in the mean time, but i cannot test new features. If you are willing to test new features, feel free to make an issue about it. If you want to contribute in any way, this would be the best for now.

# Nitroctl, a CLI NitroSense alternative for Linux, Made thanks to the linuwu-sense driver.
## WARNING
This is the only official source of nitroctl, any other github repositories/websites are completely unofficial and might be spreading malware. Please do not trust anywhere else but https://www.github.com/cani442k/nitroctl.git
## What is this?
A tool made with Python that lets you change keyboard RGB colors, thermal profiles, battery limiter and more using the Linuwu-Sense module. Currently, it works on Nitro devices only. Distro-agnostic, does not depend on systemd. Tested on Void Linux.

## Why did I make this?
[Another tool](https://github.com/PXDiv/Div-Acer-Manager-Max) that does the same thing wouldn't work on Void Linux so i decided to make my own, though mine lacks a GUI and is a bit less user friendly.

## AI Usage
As much as I absolutely despise AI, I did use it a tiny bit for fixing up typos and proper wording in the README. And thats all. I wrote all the code by hand. Nitroctl is not vibe coded. 

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
