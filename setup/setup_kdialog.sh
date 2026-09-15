#!/bin/bash


if [ -f /etc/os-release ]; then
   . /etc/os-release
fi

kdialog --msgbox "Welcome to the nitroctl setup. Click \"OK\" to continue."
if kdialog --yesno "Dependencies need to be installed in order to use nitroctl.\nClick details for a list of dependencies. \n" "python3 \n python3-pip \n git \n linux-headers" --title "Setup"; then
	dbusRef=$(kdialog --progressbar "Installing dependencies..." 0 --title "Setup")
	qdbus6 $dbusRef showCancelButton false
	if [[ "$ID" == "fedora" || "$ID_LIKE" =~ "fedora" ]]; then
		pkexec dnf install python3 python3-pip git kernel-devel kernel-headers qt6-tools -y &
		pid=$!
	elif [[ "$ID" == "arch" || "$ID_LIKE" =~ "arch" ]]; then
		pkexec pacman -S python python-pip git linux-headers qt6-base --noconfirm --needed &
		pid=$!
	elif [[ "$ID_LIKE" =~ "void" || "$ID" == "void" ]]; then
		pkexec xbps-install -S python3 python3-pip git linux-headers qt6-tools -y &
		pid=$!
	elif [[ "$ID_LIKE" =~ "debian" || "$ID_LIKE" =~ "ubuntu" || "$ID" == "debian" || "$ID" == "ubuntu" ]]; then
		pkexec apt install python3 python3-pip python-is-python3 git linux-headers-$(uname -r) qdbus-qt6 -y &
		pid=$!
	else
		kdialog --error "You are using an unsupported distro. Please check the README in the repository for manual installation. Installation aborted." --title "Setup"
		exit 1
	fi
	wait "$pid"
	qdbus6 $dbusRef org.kde.kdialog.ProgressDialog.close
else
	kdialog --error "Installation cannot continue without dependencies. Installation aborted." --title "Setup"
	exit 1
fi

if kdialog --yesno "nitroctl needs a kernel module called Linuwu-Sense. Do you want to install it? Not installing it will abort installation." --title "Setup"; then
	dbusRef=$(kdialog --progressbar "Installing Linuwu-Sense" 0 --title "Setup")
	qdbus6 $dbusRef showCancelButton false
	rm -fr /tmp/nitroctl-setup/linuwu-sense-git/
	mkdir -p /tmp/nitroctl-setup/linuwu-sense-git/
	cd /tmp/nitroctl-setup/linuwu-sense-git/
	git clone https://github.com/0x7375646F/Linuwu-Sense.git || { kdialog --error "Failed to download Linuwu-Sense. Github might be down or your internet connection might not be working properly." --title "Setup"; exit 1; }
	cd Linuwu-Sense || { kdialog --error "Failed to cd into Linuwu-Sense directory. It might not be downloaded properly." --title "Setup"; exit 1; }
	pkexec make REAL_USER="$(whoami)" install
	qdbus6 $dbusRef org.kde.kdialog.ProgressDialog.close
else
	kdialog --error "Installation aborted." --title "Setup"
	exit 1
fi
if kdialog --yesno "Are you sure you want to install nitroctl?\n This will download files from the internet, so make sure you have a proper internet connection." --title "Setup"; then
	mkdir -p "$HOME/.local/bin"
	mkdir -p "$HOME/.local/share"
	cd "$HOME/.local/share"
	git clone https://github.com/cani442k/nitroctl.git
	if ! [ -d "$HOME/.local/share/nitroctl" ] || ! [ "$(ls -A "$HOME/.local/share/nitroctl/")" ]; then
    kdialog --error "Installation failed. nitroctl couldnt be installed properly.\nCheck your internet connection, then try again." --title "Setup"
	exit 1
	fi
	chmod +x "$HOME/.local/share/nitroctl/nitroctl.sh"
	ln -sf "$HOME/.local/share/nitroctl/nitroctl.sh" "$HOME/.local/bin/nitroctl"
	kdialog --msgbox "Installation successfully finished. Installed nitroctl to $HOME/.local/share/nitroctl/" --title "Setup"
else
	kdialog --error "Installation aborted." --title "Setup"
	exit 1
fi
