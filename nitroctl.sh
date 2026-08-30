#!/bin/bash
clear
echo "Copyright (C) 2026  cani442k
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions."
sleep 2
clear

echo "Launching nitroctl..."
if [ "$EUID" -ne 0 ]; then
	echo "Root privilege required."
	exec sudo "$0" "$@"
fi
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR/main" || exit 1

python3 main.py
