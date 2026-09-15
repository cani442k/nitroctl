
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

## DEPRECATED WAY OF INSTALLATION VIA SETUP SCRIPT (For setup script ≤v1.1.26)

Current version is still v1.1.26, so use the deprecated way until v1.2.26 releases.

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

First, install kdialog, as the installation script depends on it.

On Debian/Ubuntu:

```bash
sudo apt install kdialog
```

On Fedora/Redhat/CentOS:

```bash
sudo dnf install kdialog
```

On Arch:

```bash
sudo pacman -S kdialog
```

On Void:

```bash
sudo xbps-install -S kdialog
```

After installing kdialog, download the installation script from the releases page and run it.

When installation finishes, you can run nitroctl from your terminal using:

```bash
nitroctl
```

## Installation via setup script

### Step 1: Install kdialog

On Debian/Ubuntu:

```bash
sudo apt install kdialog
```

On Fedora/Redhat/CentOS:

```bash
sudo dnf install kdialog
```

On Arch:

```bash
sudo pacman -S kdialog
```

On Void:

```bash
sudo xbps-install -S kdialog
```
### Step 2: Run the installer

Download the latest setup script from releases and run it.

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
