#!/bin/bash
clear
DBUS_REF=$(kdialog --progressbar "Copyright (C) 2026  cani442k
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions." --title "nitroctl" 0 2>/dev/null) 
qdbus $DBUS_REF showCancelButton false 2>/dev/null

sleep 3
clear
qdbus $DBUS_REF showCancelButton false 2>/dev/null
qdbus $DBUS_REF setLabelText "Launching nitroctl..." 2>/dev/null

sleep 1

qdbus $DBUS_REF close 2>/dev/null
if [ "$EUID" -ne 0 ]; then
	if [ -f "$HOME/.local/share/nitroctl/nitroctl.sh" ]; then
		exec pkexec "$HOME/.local/share/nitroctl/nitroctl.sh" "$@"
	else
		exec pkexec "$0" "$@"
	fi
fi
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR/main" || exit 1

python3 main.py
