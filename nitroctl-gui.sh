#!/bin/sh
# Abre a interface gráfica nativa (GTK4) do nitroctl.
#
# A escrita no sysfs exige privilégios administrativos. O próprio app
# (main/gtk_app.py) se reexecuta via pkexec quando aberto sem root, então
# este launcher só precisa repassar os argumentos — e do fallback sudo
# quando não há sessão gráfica (sem display o pkexec não tem como pedir
# a senha).
set -u

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
APP="$SCRIPT_DIR/main/gtk_app.py"

if [ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
    exec sudo -E python3 "$APP" "$@"
fi

exec python3 "$APP" "$@"
