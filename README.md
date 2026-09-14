# Nitroctl, a CLI NitroSense alternative for Linux, Made thanks to the linuwu-sense driver.

## What is this?
A tool made with Python that lets you change keyboard RGB colors, thermal profiles, battery limiter and more using the Linuwu-Sense module. Currently, it works on Nitro devices only. Distro-agnostic, does not depend on systemd. Tested on Void Linux and CachyOS.

## Why did I make this?
[Another tool](https://github.com/PXDiv/Div-Acer-Manager-Max) that does the same thing wouldn't work on Void Linux so i decided to make my own, though mine lacks a GUI and is a bit less user friendly.

## Quick install (one-liner)

```bash
git clone https://github.com/cani442k/nitroctl.git && cd nitroctl && ./setup/install.sh
```

Non-interactive (accepts every prompt — good for scripts and VMs):

```bash
./setup/install.sh --yes
```

CLI only, driver only, or removal:

```bash
./setup/install.sh --no-gui          # terminal interface only
./setup/install.sh --no-driver       # skip the Linuwu-Sense DKMS step
./setup/install.sh --driver-only     # only (re)install the driver via DKMS
./setup/install.sh --uninstall       # remove nitroctl + driver
```

Preview what would happen without changing anything:

```bash
./setup/install.sh --dry-run --verbose
```

Force a specific distro profile (useful in containers or derivatives):

```bash
./setup/install.sh --distro=debian
```

## How the installer works

The installer is profile-driven instead of hardcoded per distro:

1. **Detect** — reads `/etc/os-release` (`ID`, then `ID_LIKE`) and matches a profile in `setup/distros.conf`. Falls back to whichever package manager exists, then to a `generic` profile with manual instructions.
2. **Base** — installs Python, git, the matching kernel headers and, only on Clang-built kernels (like CachyOS), the LLVM toolchain.
3. **App** — clones/updates nitroctl into `~/.local/share/nitroctl` and links `nitroctl` + `nitroctl-gui` into `~/.local/bin`.
4. **GUI** — installs GTK4/Libadwaita bindings from the system packages (no virtualenv, no ~150 MB download).
5. **Driver** — clones Linuwu-Sense, applies the Clang compatibility patch (`strncpy` → `memcpy`, guarded), and registers it with DKMS, so kernel updates rebuild the module automatically.

Dialogs adapt to the desktop: `kdialog` (KDE) → `zenity` (GNOME) → `whiptail` (terminal) → plain prompts. Set `NITROCTL_UI` to force one, `NITROCTL_YES=1` for non-interactive mode.

## Supported distributions

| Profile | Distros | Package manager | Base packages | GUI packages | DKMS | Headers | Clang toolchain | Privilege |
|---|---|---|---|---|---|---|---|---|
| `cachyos` | CachyOS | pacman | python git base-devel linux-cachyos-headers | python-gobject gtk4 libadwaita | dkms | auto (flavour-aware) | clang llvm lld (auto, kernel is Clang) | sudo |
| `arch` | Arch, EndeavourOS, Manjaro | pacman | python git base-devel linux-headers | python-gobject gtk4 libadwaita | dkms | auto (flavour-aware) | clang llvm lld (if kernel is Clang) | sudo |
| `debian` | Debian, Mint, Pop!_OS | apt | python3 git build-essential dkms linux-headers-amd64 | python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 | dkms | auto (`linux-headers-$(uname -r)`) | clang llvm lld (if needed) | sudo |
| `ubuntu` | Ubuntu + flavours | apt | python3 git build-essential dkms linux-headers-generic | python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 | dkms | auto | clang llvm lld (if needed) | sudo |
| `fedora` | Fedora, RHEL, Alma, Rocky | dnf | python3 git gcc make kernel-devel kernel-headers dkms | python3-gobject gtk4 libadwaita | dkms | auto (`kernel-devel`) | clang llvm lld (if needed) | sudo |
| `opensuse` | Leap, Tumbleweed | zypper | python3 git gcc make kernel-devel kernel-default-devel dkms | python3-gobject gtk4 libadwaita | dkms | auto | clang llvm lld (if needed) | sudo |
| `void` | Void (glibc/musl) | xbps | python3 git base-devel linux-headers dkms | python3-gobject gtk4 libadwaita | dkms | auto | clang llvm lld (if needed) | sudo |
| `alpine` | Alpine | apk | python3 git build-base linux-headers dkms | python3 gobject-introspection gtk4.0 libadwaita | dkms | `linux-lts-dev` | clang llvm lld (if needed) | doas |
| `gentoo` | Gentoo | emerge | dev-lang/python dev-vcs/git sys-kernel/linux-headers sys-kernel/dkms | dev-python/pygobject gui-libs/gtk gui-libs/libadwaita | sys-kernel/dkms | manual (your kernel sources) | llvm-core/clang llvm-core/llvm llvm-core/lld | sudo |
| `generic` | anything else | — | install python3 + git by hand | install GTK4 bindings by hand | — | manual | manual | su |

Notes:

* **Headers follow the running kernel.** On Arch flavours the installer maps `uname -r` to the right `-headers` package (`linux-cachyos-headers`, `linux-zen-headers`, …). On Debian/Ubuntu it uses `linux-headers-$(uname -r)`; on Fedora/RHEL, `kernel-devel`.
* **LLVM only when needed.** The Clang toolchain is installed only if the running kernel was built with Clang (`CONFIG_CC_IS_CLANG=y`) and `clang` is missing.
* **Alpine** uses `doas` instead of `sudo` and OpenRC instead of systemd — the driver's systemd unit does not apply there; load the module via `/etc/modules` or `modprobe` after boot.
* **Gentoo** assumes your kernel sources are already configured; headers come from them.

## Prerequisites

This tool depends on python and the [Linuwu-Sense](https://github.com/0x7375646F/Linuwu-Sense) module. The setup script installs and registers it via DKMS automatically; the manual guide below is only for special cases.

The graphical interface (`nitroctl-gui`) is a native GTK4 + Libadwaita app and uses the system Python with PyGObject — no virtualenv, no extra downloads. Install the bindings for your distro (the setup script offers to do this — see the table above).

## Installation via setup script

Just run it — it detects your distro, installs dependencies, the app, the GUI bindings and the driver:

```bash
./setup/install.sh
```

When installation finishes, you can run nitroctl from your terminal using:

```bash
nitroctl
```

## Manual installation

First, install Linuwu-Sense the same way its done above. Then, proceed with the installation as described below.

### Step 1: Install dependencies

The required dependencies are python3 and git. Package names may be different on your distro — see the table above for the exact packages per distro.

For Debian:

```bash
sudo apt install python3 git
```

For Fedora:

```bash
sudo dnf install python3 git
```

For Arch:

```bash
sudo pacman -S python git
```

For Void:

```bash
sudo xbps-install -S python3 git
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

## Arch Linux (and Arch-based distributions)

Everything above applies to Arch; the setup script picks the `arch` (or `cachyos`) profile automatically. Two details matter on Arch-family systems, especially those that ship Clang-built kernels such as CachyOS:

* **Kernel headers**: installed automatically, flavour-aware (`linux-headers`, `linux-cachyos-headers`, `linux-zen-headers`, … depending on `uname -r`).
* **Clang-built kernels**: Linuwu-Sense does not compile with GCC on those kernels (the kernel itself was built with Clang, and GCC rejects its flags). The installer detects this and builds with `LLVM=1` through DKMS.

The setup script registers Linuwu-Sense with DKMS (`setup/dkms.conf`), applying the Clang compatibility fix (`strncpy` → `memcpy`) at install time. From then on, every kernel update rebuilds and reinstalls the module automatically — no manual recompilation.

## Graphical interface

`nitroctl-gui` offers the same functions as the text menu in a native GTK4 window:

```bash
nitroctl-gui
```

It elevates itself: opened as a normal user it asks for your password through polkit (graphical prompt) or `sudo` (terminal fallback), so there is no need to prefix it with `sudo` yourself. Opened without privileges it still shows the driver state read-only.

Both interfaces share the same driver code (`main/nitro_core.py`), so features and validation rules stay in one place.

## To Do

* [❌] Keyboard RGB
* [✅] ~~GUI~~
* [❌] CPU&GPU Temparatures on main menu
* [✅] ~~Finish the installation guide~~
* [✅] ~~Configuration Save/Load function~~
