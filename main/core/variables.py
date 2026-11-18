#!/usr/bin/env python3
sudo_user = os.environ.get("SUDO_USER")
real_home = Path(f"/home/{sudo_user}") if sudo_user else Path.home()
configs_dir = real_home / ".config" / "nitroctl"
sysfs_path = Path("/sys/module/linuwu_sense/drivers/platform:acer-wmi/acer-wmi/nitro_sense")
linuwusense_dir = "/sys/devices/platform/acer-wmi"
