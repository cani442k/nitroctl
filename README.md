# Nitroctl, a CLI NitroSense alternative for Linux, Made thanks to the linuwu-sense driver.

## What is this?
A tool made with Python that lets you change keyboard RGB colors, thermal profiles, battery limiter and more using the Linuwu-Sense module. Currently, it works on Nitro devices only. Distro-agnostic, does not depend on systemd. Tested on Void Linux.

## Why did I make this?
[Another tool](https://github.com/PXDiv/Div-Acer-Manager-Max) that does the same thing wouldn't work on Void Linux so i decided to make my own, though mine lacks a GUI and is a bit less user friendly.

## Prerequisites

This tool depends on python and the [Linuwu-Sense](https://github.com/0x7375646F/Linuwu-Sense) module. Installation guide of Linuwu-Sense can be found on their repository.

## Installation

### Step 1: Install Linuwu-Sense

First, install headers for your kernel:

For Debian/Ubuntu:

```bash
sudo apt install -y linux-headers-amd64
```

For Fedora/RedHat/CentOS:

```bash
sudo dnf install kernel-devel
```

For Arch:

```bash
sudo pacman -S linux-headers
```
For Void:
```bash
sudo xbps-install -S linux-headers
```
After installing headers, clone the Linuwu-Sense repository and install the module:

```bash
git clone https://github.com/0x7375646F/Linuwu-Sense.git
cd Linuwu-Sense
make install
```

### Step 2: Install nitroctl
Work in progress

