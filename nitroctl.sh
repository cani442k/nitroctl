#!/bin/bash
echo "Launching nitroctl..."
if [ "$EUID" -ne 0 ]; then
	echo "Root privilege required."
	exec sudo "$0" "$@"
fi
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR/main" || exit 1

python3 main.py
