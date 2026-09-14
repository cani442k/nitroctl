#!/bin/sh
# Abre a interface gráfica nativa (GTK4) do nitroctl.
#
# A escrita no sysfs exige privilégios administrativos, então o programa roda
# com eles: se já estiver como root, abre direto; se houver sessão gráfica
# com polkit, eleva via pkexec (diálogo gráfico de senha); caso contrário,
# usa sudo no terminal.
set -u

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
APP="$SCRIPT_DIR/main/gtk_app.py"

if [ "$(id -u)" -eq 0 ]; then
    exec python3 "$APP" "$@"
fi

if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] && command -v pkexec >/dev/null 2>&1; then
    exec pkexec python3 "$APP" "$@"
fi

exec sudo -E python3 "$APP" "$@"
