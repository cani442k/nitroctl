# nitroctl, a TUI based NitroSense alternative for Linux, written with Python.
## WARNING
This is the only official source of nitroctl, any other github repositories/websites are completely unofficial and might be spreading malware. Please do not trust anywhere else but https://www.github.com/cani442k/nitroctl.git
## Want to contribute? I need some beta testers!
I have recently sold the Acer Nitro 16 I wrote nitroctl for. That does not mean I'm stopping development. Development will continue on the beta branch. If you have an Acer Nitro laptop and want to contribute to this project, now would be the best time to do so, and you don't even need to know how to code. If you want to be a beta tester, just create an issue about it on the repository. Thanks for using nitroctl!
## What is nitroctl?
nitroctl is a TUI utility to configure thermal profiles, battery limiter and more on Acer Nitro laptops (and Acer Nitro laptops only, nitroctl does not work on Acer Predator laptops for now) using the awesome work of [0x7375646F](https://github.com/0x7375646F) with [Linuwu-Sense](https://github.com/0x7375646F/Linuwu-Sense).
## Why did I make nitroctl?
I made this utility because [another app](https://github.com/PXDiv/Div-Acer-Manager-Max) I used to use required systemd and I wanted to use Void Linux. So I made my own version. Nitroctl lacks a GUI and keyboard RGB configuration (for now) though.
## I have been seeing a lot of NitroSense alternatives lately and all of those are Vibecoded (AI generated). Is this one of those?
No! I am heavily anti-AI and I didnt vibecode NitroSense at all. It would be a lie to say I haven't used AI at all during the process of making it, but I will confirm that none of the code is AI generated. I wrote all of the code myself. The only part where I used AI was fixing up typos and generally polishing up the old version of the README. The new version (which you're reading right now) is also written all by me.

TL;DR: Nitroctl is not made by AI.
# Installation guide
For most users, just downloading and running the latest installer script from github releases should be enough. If you get an error with the installer script, you can install nitroctl manually. Below are the instructions for doing so:
## Step 1 - Installing dependencies
First, you need to install the dependencies for nitroctl. These are python3, python3-pip, git (package names may vary) and of course, Linuwu-Sense.

Below are the commands to install the dependencies on Debian/Ubuntu, Fedora, Arch Linux and Void Linux.

For Debian/Ubuntu:

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

Once these are done, install Linuwu-Sense. The guide to do so is found on [its repository.](https://github.com/0x7375646F/Linuwu-Sense#-installation)

After you install Linuwu-Sense, move to Step 2.
## Step 2 - Installing nitroctl
There are two options for installing nitroctl, portable installation and user installation. I recommend the user installation method as it links nitroctl to ~/.local/bin/ which should also add it to the user's PATH on most distros.
### Option 1 - User Installation (recommended)
Work in progress
### Option 2 - Portable Installation (not recommended)
Simply cd into the directory you want to download nitroctl to, then clone the github repository.

```bash
cd /your/destination/
git clone https://github.com/cani442k/nitroctl.git
```
When you want to run it, cd into the installed location and run nitroctl.sh:

```bash
cd /your/destination/nitroctl/
chmod +x nitroctl.sh
./nitroctl.sh
```
# To Do


* [❌] Keyboard RGB
* [❌] CPU&GPU Temparatures on main menu
* [❌] Write uninstallation script
* [❌] Write auto-update manager
* [❌] .desktop file to show up in app launchers
* [❌] Finish the installation guide
* [✅] ~~Configuration Save/Load function~~