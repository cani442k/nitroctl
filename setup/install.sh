#!/bin/bash


if [ -f /etc/os-release ]; then
   . /etc/os-release
fi
kdialog --msgbox "Welcome to the nitroctl setup. Click \"OK\" to continue."
if kdialog --yesno "Dependencies need to be installed in order to use nitroctl.\nClick details for a list of dependencies." "python3 \n python3-pip \n git" --title "Setup"; then

	if [[ "$ID" == "fedora" || "$ID_LIKE" =~ "fedora" ]]; then
		pkexec dnf install python3 python3-pip git -y
	elif [[ "$ID" == "arch" || "$ID_LIKE" =~ "arch" ]]; then
		pkexec pacman -S python python-pip git --noconfirm --needed
	elif [[ "$ID_LIKE" =~ "void" || "$ID" == "void" ]]; then
		pkexec xbps-install -S python3 python3-pip git -y
	elif [[ "$ID_LIKE" =~ "debian" || "$ID_LIKE" =~ "ubuntu" || "$ID" == "debian" || "$ID" == "ubuntu" ]]; then
		pkexec apt install python3 python3-pip python-is-python3 git -y
	else
		kdialog --error "You are using an unsupported distro. Please check the README in the repository for manual installation. Installation aborted." --title "Setup"
		exit 1
	fi
else
	kdialog --error "Installation cannot continue without dependencies. Installation aborted." --title "Setup"
	exit 1
fi

if kdialog --yesno "Are you sure you want to install nitroctl?\n This will download files from the internet, so make sure you have a proper internet connection." --title "Setup"; then
	mkdir -p "$HOME/.local/bin"
	mkdir -p "$HOME/.local/share"
	cd "$HOME/.local/share"
	git clone http://github.com/cani442k/nitroctl.git
	ln -sf "$HOME/.local/share/nitroctl/nitroctl.sh" "$HOME/.local/bin/nitroctl"
	kdialog --msgbox "Installation successfully finished. Installed nitroctl to $HOME/.local/share/nitroctl/" --title "Setup"
else
	kdialog --error "Installation aborted." --title "Setup"
fi
