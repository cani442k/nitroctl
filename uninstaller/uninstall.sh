#!/bin/bash
if [[ $(uname -s) != "Linux" ]]; then
	echo "ERROR: Fatal: nitroctl is a Linux utility. You must run this script on Linux."
	exit 1
fi
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Fatal: Script detected to be running as root. This will cause a fail in uninstallation. Do not run the script with sudo."
    exit 1
fi
clear
echo "Welcome to the nitroctl uninstaller!"
echo "This script will uninstall nitroctl and optionally delete nitroctl configuration from your system."
read -p "Are you sure you want to proceed? [y/n] " confirmuninstall
case "$confirmuninstall" in
	y|Y )
		echo "Proceeding with uninstallation."
		;;
	n|N )
		echo "Uninstallation aborted."
		exit 1
		;;
	* )
        echo "ERROR: Fatal: Invalid choice. Uninstallation aborted."
        exit 1
		;;
esac
echo "Uninstallation will start in:"
echo "3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1
echo
echo
echo
echo "Scanning for nitroctl..."
if [ -d "$HOME/.local/share/nitroctl"]; then
	echo "Found nitroctl at $HOME/.local/share/nitroctl, removing..."
	rm -fr "$HOME/.local/share/nitroctl"
	echo "nitroctl removed successfully!"
else

	echo "nitroctl not installed, so not removed."
fi
echo
echo "Scanning for nitroctl configurations..."
if [ -d "$HOME/.config/nitroctl"]; then
	echo "Found nitroctl configuration at $HOME/.config/nitroctl!"
	read -p "Do you want to remove nitroctl configuration? [y/n] " confirmconfig
	case "$confirmconfig" in
		y|Y )
			echo "Removing nitroctl configuration..."
			rm -fr "$HOME/.config/nitroctl"
			;;
		n|N )
			echo "Keeping nitroctl configuration."
			;;
		* )
			echo "ERROR: Fatal: Invalid choice. Configuration will not be removed."
			;;
	esac
else
	echo "nitroctl configuration not found, so not removed."
fi
echo "nitroctl uninstallation has completed. If you want to remove Linuwu-Sense too, consult its manual."
exit 0
