#!/bin/bash

if [ -f /etc/os-release ]; then
   . /etc/os-release
fi

echo "Welcome to the nitroctl installer!"
sleep 1
read -p "Some dependencies need to be installed in order to use nitroctl. These are python, git and the headers for your kernel. Do you want to install them? Not installing will abort installation. [y/n] " depsconfirm
echo
case "$depsconfirm" in 
    y|Y )
        echo "Installing dependencies..."
        sleep 1
        echo
        if [[ "$ID" == "fedora" || "$ID_LIKE" =~ "fedora" ]]; then
		    sudo dnf install python3 python3-pip git kernel-devel kernel-headers -y 
	    elif [[ "$ID" == "arch" || "$ID_LIKE" =~ "arch" ]]; then
		    sudo pacman -S python python-pip git linux-headers --noconfirm --needed
	    elif [[ "$ID_LIKE" =~ "void" || "$ID" == "void" ]]; then
		    sudo xbps-install -S python3 python3-pip git linux-headers -y
	    elif [[ "$ID_LIKE" =~ "debian" || "$ID_LIKE" =~ "ubuntu" || "$ID" == "debian" || "$ID" == "ubuntu" ]]; then
		    sudo apt-get install python3 python3-pip python-is-python3 git linux-headers-$(uname -r) -y
	    else
		    echo "ERROR: Fatal: You are using an unsupported distro. Please check the README in the repository for manual installation. Installation aborted."
		    exit 1
	    fi
        ;;
    n|N )
        echo "ERROR: Fatal: Installation aborted by user."
        exit 1
        ;;
    * )
        echo "ERROR: Fatal: Invalid choice."
        exit 1
esac
sleep 1
echo
read -p "nitroctl requires a kernel module called Linuwu-Sense to work. Do you want to install it? Installation will cancel otherwise. [y/n]" linuwuchoice
case "$linuwuchoice" in 
	y|Y )
		sleep 1
		echo "Installing linuwu-sense."
		rm -fr /tmp/nitroctl-setup/linuwu-sense-git/
		mkdir -p /tmp/nitroctl-setup/linuwu-sense-git/
		cd /tmp/nitroctl-setup/linuwu-sense-git/
		git clone https://github.com/0x7375646F/Linuwu-Sense.git
		cd Linuwu-Sense || { echo "ERROR: Fatal: Linuwu-Sense wasnt downloaded properly. Exiting." ; exit 1; }
		make install
		;;
	n|N )
		echo "ERROR: Fatal: Installation aborted by user"
		exit 1
		;;
	* )
		echo "ERROR: Fatal: Invalid option."
		exit 1
esac
echo "Nitroctl installation will commence in:"
echo "3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1
echo "Installation started."
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.local/share"
cd "$HOME/.local/share/"
git clone https://www.github.com/cani442k/nitroctl.git
sleep 1
echo "Verifying nitroctl files..."
if ! [ -d "$HOME/.local/share/nitroctl" ] || ! [ "$(ls -A "$HOME/.local/share/nitroctl/")" ]; then
echo -e "ERROR: Fatal: Missing files. nitroctl couldnt be installed properly.\nCheck your internet connection, then try again."
exit 1
fi
chmod +x "$HOME/.local/share/nitroctl/nitroctl.sh"
ln -sf "$HOME/.local/share/nitroctl/nitroctl.sh" "$HOME/.local/bin/nitroctl"
echo "Installation successfully finished. No errors reported."
echo "Installed nitroctl to $HOME/.local/bin/nitroctl"
echo "You can now run nitroctl from anywhere by running \"nitroctl\" in your terminal."
sleep 1
exit 0
    
