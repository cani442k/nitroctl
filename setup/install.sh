#!/usr/bin/env bash
#
# Instalador do nitroctl — distro-agnóstico, dirigido por perfis.
#
# Esquema:
#   1. detecta a distro via /etc/os-release (ID, depois ID_LIKE) e casa com um
#      perfil de setup/distros.conf (--distro=ID força um perfil);
#   2. instala base (python+git+headers), GUI GTK4 e DKMS conforme o perfil;
#   3. instala o nitroctl (CLI + GUI) em ~/.local;
#   4. registra o Linuwu-Sense no DKMS com o patch Clang (LLVM=1).
#
# Uso:
#   ./install.sh [opções]
#
# Opções:
#   --yes              responde "sim" a todas as perguntas (não-interativo)
#   --no-deps          pula a instalação de dependências da base
#   --no-gui           pula as dependências da GUI (só CLI)
#   --no-driver        pula a etapa DKMS/driver
#   --driver-only      só executa a etapa DKMS/driver e sai
#   --uninstall        remove nitroctl + driver e sai
#   --distro=ID        força o perfil ID de setup/distros.conf
#   --dry-run          mostra o que seria feito, sem executar nada
#   --verbose          log detalhado (perfil, comandos, decisões)
#   -h, --help         mostra esta ajuda e sai
#
# Variáveis de ambiente:
#   NITROCTL_UI=kdialog|zenity|whiptail|plain   força o backend de diálogo
#   NITROCTL_YES=1                              equivale a --yes
set -u

VERSION="2.0.0"
REPO_URL="https://github.com/eltonacosta/nitroctl.git"
DRIVER_URL="https://github.com/0x7375646F/Linuwu-Sense.git"
SRC_DIR="$HOME/.local/share/nitroctl"
BIN_DIR="$HOME/.local/bin"
DKMS_NAME="linuwu_sense"
DKMS_VERSION="1.0"
TITLE="nitroctl"

# ------------------------------------------------------------------ opções
OPT_YES=0 OPT_NO_DEPS=0 OPT_NO_GUI=0 OPT_NO_DRIVER=0
OPT_DRIVER_ONLY=0 OPT_UNINSTALL=0 OPT_DISTRO="" OPT_DRY_RUN=0 OPT_VERBOSE=0

usage() {
    sed -n '2,/^set -u/p' "$0" | sed 's/^# \?//'
}

log() {
    [ "$OPT_VERBOSE" -eq 1 ] && printf '[nitroctl] %s\n' "$1" >&2
    return 0
}

while [ $# -gt 0 ]; do
    case "$1" in
        --yes) OPT_YES=1 ;;
        --no-deps) OPT_NO_DEPS=1 ;;
        --no-gui) OPT_NO_GUI=1 ;;
        --no-driver) OPT_NO_DRIVER=1 ;;
        --driver-only) OPT_DRIVER_ONLY=1 ;;
        --uninstall) OPT_UNINSTALL=1 ;;
        --distro=*) OPT_DISTRO="${1#--distro=}" ;;
        --dry-run) OPT_DRY_RUN=1 ;;
        --verbose) OPT_VERBOSE=1 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Opção desconhecida: $1 (use --help)" >&2; exit 2 ;;
    esac
    shift
done
[ -n "${NITROCTL_YES:-}" ] && OPT_YES=1

# ---------------------------------------------------------------- diálogos
UI=""
detect_ui() {
    if [ -n "${NITROCTL_UI:-}" ]; then UI="$NITROCTL_UI"; return; fi
    for candidate in kdialog zenity whiptail; do
        if command -v "$candidate" >/dev/null 2>&1; then UI="$candidate"; return; fi
    done
    UI="plain"
}

msg() {
    case "$UI" in
        kdialog) kdialog --msgbox "$1" --title "$TITLE" ;;
        zenity) zenity --info --title="$TITLE" --text="$1" --width=480 ;;
        whiptail) whiptail --title "$TITLE" --msgbox "$1" 18 76 ;;
        *) printf '\n%s\n' "$1" >&2 ;;
    esac
}

err() {
    case "$UI" in
        kdialog) kdialog --error "$1" --title "$TITLE" ;;
        zenity) zenity --error --title="$TITLE" --text="$1" --width=480 ;;
        whiptail) whiptail --title "$TITLE" --msgbox "$1" 18 76 ;;
        *) printf '\nERRO: %s\n' "$1" >&2 ;;
    esac
}

ask_yn() {
    if [ "$OPT_YES" -eq 1 ]; then log "auto-sim: $1"; return 0; fi
    case "$UI" in
        kdialog) kdialog --yesno "$1" --title "$TITLE" ;;
        zenity) zenity --question --title="$TITLE" --text="$1" --width=480 ;;
        whiptail) whiptail --title "$TITLE" --yesno "$1" 18 76 ;;
        *)
            local answer
            printf '\n%s [s/N] ' "$1" >&2
            read -r answer || return 1
            case "$answer" in [sSyY]*) return 0 ;; *) return 1 ;; esac
            ;;
    esac
}

# ------------------------------------------------- perfis por distribuição
# Carrega setup/distros.conf e resolve o perfil: --distro > ID > ID_LIKE > pm.
DISTRO_FILE=""
find_distros_conf() {
    for candidate in "$SRC_DIR/setup/distros.conf" "$(dirname "$(readlink -f "$0")")/distros.conf"; do
        if [ -f "$candidate" ]; then DISTRO_FILE="$candidate"; return 0; fi
    done
    return 1
}

trim() { printf '%s' "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'; }

P_PM=""; P_BASE=""; P_GUI=""; P_DKMS=""; P_HEADERS=""; P_LLVM=""; P_SUDO=""; P_NOTES=""
P_ID=""; DISTRO_NAME="distribuição não identificada"

load_profile() {
    local want="$1" line id pm base gui dkms headers llvm sudo notes
    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in \#*|"") continue ;; esac
        id="$(trim "$(printf '%s' "$line" | cut -d'|' -f1)")"
        [ "$id" = "$want" ] || continue
        pm="$(trim "$(printf '%s' "$line" | cut -d'|' -f2)")"
        base="$(trim "$(printf '%s' "$line" | cut -d'|' -f3)")"
        gui="$(trim "$(printf '%s' "$line" | cut -d'|' -f4)")"
        dkms="$(trim "$(printf '%s' "$line" | cut -d'|' -f5)")"
        headers="$(trim "$(printf '%s' "$line" | cut -d'|' -f6)")"
        llvm="$(trim "$(printf '%s' "$line" | cut -d'|' -f7)")"
        sudo="$(trim "$(printf '%s' "$line" | cut -d'|' -f8)")"
        notes="$(trim "$(printf '%s' "$line" | cut -d'|' -f9)")"
        P_ID="$id"; P_PM="$pm"; P_BASE="$base"; P_GUI="$gui"
        P_DKMS="$dkms"; P_HEADERS="$headers"; P_LLVM="$llvm"
        P_SUDO="$sudo"; P_NOTES="$notes"
        return 0
    done < "$DISTRO_FILE"
    return 1
}

profile_has_pm() {
    case "$P_PM" in
        pacman) command -v pacman >/dev/null 2>&1 ;;
        apt) command -v apt >/dev/null 2>&1 ;;
        dnf) command -v dnf >/dev/null 2>&1 ;;
        zypper) command -v zypper >/dev/null 2>&1 ;;
        xbps) command -v xbps-install >/dev/null 2>&1 ;;
        apk) command -v apk >/dev/null 2>&1 ;;
        emerge) command -v emerge >/dev/null 2>&1 ;;
        *) return 1 ;;
    esac
}

resolve_profile() {
    find_distros_conf || { err "setup/distros.conf não encontrado."; return 1; }
    if [ -n "$OPT_DISTRO" ]; then
        load_profile "$OPT_DISTRO" || { err "Perfil '$OPT_DISTRO' não existe em setup/distros.conf."; return 1; }
        log "perfil forçado: $P_ID"
        return 0
    fi
    local os_id="" os_like="" os_name="distribuição não identificada" candidate
    if [ -r /etc/os-release ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        os_id="${ID:-}"; os_like="${ID_LIKE:-}"; os_name="${PRETTY_NAME:-${NAME:-$os_id}}"
    fi
    DISTRO_NAME="$os_name"
    log "os-release: ID=$os_id ID_LIKE=$os_like"
    for candidate in $os_id $os_like; do
        if load_profile "$candidate" && profile_has_pm; then
            log "perfil: $P_ID ($P_NOTES)"
            return 0
        fi
    done
    # Fallback: primeiro perfil cujo gerenciador exista no sistema.
    for candidate in arch debian fedora opensuse void alpine gentoo; do
        if load_profile "$candidate" && profile_has_pm; then
            log "perfil por gerenciador: $P_ID"
            return 0
        fi
    done
    load_profile "generic" || { err "Perfil 'generic' ausente em setup/distros.conf."; return 1; }
    log "perfil genérico (sem gerenciador conhecido)"
    return 0
}

# ------------------------------------------------------------ comandos base
INSTALL_CMD=""
SUDO="sudo"

build_install_cmd() {
    case "$P_PM" in
        pacman) INSTALL_CMD="sudo pacman -S --noconfirm --needed" ;;
        apt) INSTALL_CMD="sudo apt install -y" ;;
        dnf) INSTALL_CMD="sudo dnf install -y" ;;
        zypper) INSTALL_CMD="sudo zypper install -y" ;;
        xbps) INSTALL_CMD="sudo xbps-install -S -y" ;;
        apk) INSTALL_CMD="sudo apk add" ;;
        emerge) INSTALL_CMD="sudo emerge --ask=n" ;;
        *) INSTALL_CMD="" ;;
    esac
    case "$P_SUDO" in
        doas) SUDO="doas" ;;
        su-c) SUDO="su -c" ;;
        *) SUDO="sudo" ;;
    esac
    if ! command -v "${SUDO%% *}" >/dev/null 2>&1; then
        log "elevador '$SUDO' ausente; usando sudo"
        SUDO="sudo"
    fi
}

run_root() {
    # Executa comando com privilégio (respeita --dry-run).
    if [ "$OPT_DRY_RUN" -eq 1 ]; then printf '[dry-run] %s %s\n' "$SUDO" "$*" >&2; return 0; fi
    if [ "$(id -u)" -eq 0 ]; then "$@"; else $SUDO "$@"; fi
}

run_install() {
    # Instala pacotes via gerenciador (respeita --dry-run).
    if [ "$OPT_DRY_RUN" -eq 1 ]; then printf '[dry-run] %s %s\n' "$INSTALL_CMD" "$*" >&2; return 0; fi
    # shellcheck disable=SC2086
    $INSTALL_CMD "$@" || return 1
}

need_pkgs() {
    # Lista pacotes do perfil ainda não instalados (heurística por binário).
    # Uso: need_pkgs "pkg1 pkg2" -> ecoa somente os ausentes.
    local pkg missing=""
    for pkg in $1; do
        case "$pkg" in
            python|python3) command -v python3 >/dev/null 2>&1 || missing="$missing $pkg" ;;
            git) command -v git >/dev/null 2>&1 || missing="$missing $pkg" ;;
            dkms|cachyos-dkms) command -v dkms >/dev/null 2>&1 || missing="$missing $pkg" ;;
            *) missing="$missing $pkg" ;;
        esac
    done
    printf '%s' "$missing"
}

# ------------------------------------------------- cabeçalhos do kernel
# O DKMS só recompila sozinho se os headers do kernel rodando existirem.
# P_HEADERS diz como descobri-los: auto:<pm> resolve para o pacote certo.
resolve_headers_pkg() {
    local kver
    kver="$(uname -r)"
    case "$P_HEADERS" in
        auto:pacman)
            if [ -d "/usr/lib/modules/$kver/build" ]; then printf ''; return 0; fi
            case "$kver" in
                *-cachyos) printf 'linux-cachyos-headers' ;;
                *-lts*) printf 'linux-lts-headers' ;;
                *-zen*) printf 'linux-zen-headers' ;;
                *-hardened*) printf 'linux-hardened-headers' ;;
                *-lts) printf 'linux-lts-headers' ;;
                *) printf 'linux-headers' ;;
            esac
            ;;
        auto:apt)
            if [ -d "/lib/modules/$kver/build" ]; then printf ''; return 0; fi
            printf 'linux-headers-%s' "$kver"
            ;;
        auto:dnf|auto:zypper)
            if [ -d "/lib/modules/$kver/build" ]; then printf ''; return 0; fi
            printf 'kernel-devel'
            ;;
        auto:xbps)
            if [ -d "/usr/src/linux-headers-$kver" ] || [ -d "/lib/modules/$kver/build" ]; then printf ''; return 0; fi
            printf 'linux-headers'
            ;;
        auto:apk)
            printf 'linux-lts-dev'
            ;;
        *) printf '' ;;
    esac
}

kernel_is_clang() {
    local kdir="/lib/modules/$(uname -r)/build/.config"
    [ -r "$kdir" ] && grep -q "^CONFIG_CC_IS_CLANG=y" "$kdir"
}

# -------------------------------------------------------------- instalação
install_packages() {
    local label="$1" pkgs="$2" missing
    [ -z "$pkgs" ] && return 0
    missing="$(need_pkgs "$pkgs")"
    # Headers e LLVM entram na conta mesmo sem binário para checar.
    [ -z "$(trim "$missing")" ] && { log "$label: tudo presente"; return 0; }
    if [ -z "$INSTALL_CMD" ]; then
        err "Pacotes necessários ($label):$missing

Nenhum gerenciador suportado. Instale manualmente e rode com --no-deps."
        return 1
    fi
    if ask_yn "Instalar dependências ($label):$missing

Comando: $INSTALL_CMD$missing"; then
        # shellcheck disable=SC2086
        run_install $missing || { err "A instalação de ($label) falhou."; return 1; }
    else
        err "Instalação interrompida (faltam: $label)."
        return 1
    fi
}

install_base() {
    [ "$OPT_NO_DEPS" -eq 1 ] && { log "base pulada (--no-deps)"; return 0; }
    local pkgs="$P_BASE" headers
    headers="$(resolve_headers_pkg)"
    [ -n "$headers" ] && pkgs="$pkgs $headers"
    if kernel_is_clang && [ -n "$P_LLVM" ]; then
        if ! command -v clang >/dev/null 2>&1; then
            log "kernel Clang detectado; adicionando toolchain: $P_LLVM"
            pkgs="$pkgs $P_LLVM"
        else
            log "kernel Clang, toolchain já presente"
        fi
    fi
    install_packages "base" "$pkgs"
}

install_nitroctl() {
    mkdir -p "$BIN_DIR"
    mkdir -p "$(dirname "$SRC_DIR")"
    if [ "$OPT_DRY_RUN" -eq 1 ]; then
        printf '[dry-run] clonar/atualizar %s em %s; linkar nitroctl + nitroctl-gui em %s\n' "$REPO_URL" "$SRC_DIR" "$BIN_DIR" >&2
        return 0
    fi
    if [ -d "$SRC_DIR/.git" ]; then
        msg "O nitroctl já está em $SRC_DIR; atualizando com git pull."
        git -C "$SRC_DIR" pull --ff-only || { err "Não foi possível atualizar o repositório em $SRC_DIR."; return 1; }
    elif [ -d "$SRC_DIR" ] && [ -n "$(ls -A "$SRC_DIR" 2>/dev/null)" ]; then
        # Diretório de uma instalação anterior (clone do upstream ou cópia):
        # sincroniza com a árvore que contém este install.sh, que é a fonte
        # canônica dos arquivos que as etapas seguintes (dkms.conf, service)
        # esperam encontrar em $SRC_DIR.
        msg "$SRC_DIR já existe; sincronizando com a árvore atual."
        local self_dir
        self_dir="$(dirname "$(readlink -f "$0")")/.."
        if [ -d "$self_dir/setup" ] && [ "$self_dir" != "$SRC_DIR" ]; then
            cp -r "$self_dir/." "$SRC_DIR/" || { err "Não foi possível sincronizar $SRC_DIR."; return 1; }
            rm -rf "$SRC_DIR/.git"
        fi
    else
        git clone "$REPO_URL" "$SRC_DIR" || { err "Não foi possível baixar o nitroctl. Verifique a conexão e tente de novo."; return 1; }
    fi
    for script in nitroctl.sh nitroctl-gui.sh; do
        [ -f "$SRC_DIR/$script" ] && chmod +x "$SRC_DIR/$script"
    done
    ln -sf "$SRC_DIR/nitroctl.sh" "$BIN_DIR/nitroctl"
    ln -sf "$SRC_DIR/nitroctl-gui.sh" "$BIN_DIR/nitroctl-gui"

    # Entrada no menu de aplicativos + ícone (modo gráfico).
    # O Exec usa caminho absoluto: ~/.local/bin pode não estar no PATH que
    # o lançador gráfico enxerga (comum em Debian/Ubuntu, Fedora, openSUSE).
    mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor/scalable/apps"
    if [ -f "$SRC_DIR/setup/nitroctl.desktop" ]; then
        sed "s|^Exec=nitroctl-gui|Exec=$BIN_DIR/nitroctl-gui|" \
            "$SRC_DIR/setup/nitroctl.desktop" > "$HOME/.local/share/applications/nitroctl.desktop"
    fi
    if [ -f "$SRC_DIR/setup/nitroctl.svg" ]; then
        cp "$SRC_DIR/setup/nitroctl.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/nitroctl.svg"
    fi
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    fi
    msg "nitroctl instalado em $SRC_DIR, com os comandos 'nitroctl' e 'nitroctl-gui' em $BIN_DIR e entrada no menu de aplicativos."
}

install_gui_deps() {
    if [ "$OPT_NO_GUI" -eq 1 ]; then
        log "GUI pulada (--no-gui)"
        msg "Interface gráfica não instalada (--no-gui). O 'nitroctl' de terminal continua funcionando."
        return 0
    fi
    if python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')" 2>/dev/null; then
        msg "Interface gráfica pronta (GTK4 nativo, sem downloads extras). Abra com 'nitroctl-gui'."
        return 0
    fi
    install_packages "GUI (GTK4)" "$P_GUI" || return 1
    msg "Interface gráfica pronta. Abra com 'nitroctl-gui'."
}

install_driver_dkms() {
    if [ "$OPT_NO_DRIVER" -eq 1 ]; then
        log "driver pulado (--no-driver)"
        return 0
    fi
    if [ -z "$P_DKMS" ] || [ "$P_DKMS" = "(none)" ]; then
        msg "AVISO: este perfil não prevê DKMS. Instale o Linuwu-Sense manualmente ($DRIVER_URL) e recompile a cada atualização de kernel."
        return 0
    fi
    if ! command -v dkms >/dev/null 2>&1; then
        install_packages "DKMS" "$P_DKMS" || return 1
    fi

    local dkms_src="/usr/src/${DKMS_NAME}-${DKMS_VERSION}"
    local workdir
    if [ "$OPT_DRY_RUN" -eq 1 ]; then
        printf '[dry-run] clonar %s, aplicar patch Clang, copiar para %s, dkms add+autoinstall\n' "$DRIVER_URL" "$dkms_src" >&2
        return 0
    fi
    workdir="$(mktemp -d)" || { err "Não foi possível criar diretório temporário."; return 1; }
    git clone --depth 1 "$DRIVER_URL" "$workdir/Linuwu-Sense" || {
        rm -rf "$workdir"
        err "Não foi possível baixar o Linuwu-Sense. Verifique a conexão e tente de novo."
        return 1
    }

    if grep -q "strncpy" "$workdir/Linuwu-Sense/src/linuwu_sense.c"; then
        python3 - "$workdir/Linuwu-Sense/src/linuwu_sense.c" <<'PYEOF' || {
import sys
path = sys.argv[1]
text = open(path).read()
assert text.count("strncpy(") == 3, "padrão strncpy mudou no upstream; revise o patch"
text = text.replace("strncpy(", "memcpy(")
text = text.replace("if(input[len-1]", "if(len && input[len-1]")
text = text.replace("if(input_buf[len-1]", "if(len && input_buf[len-1]")
text = text.replace("if(str_buf[len-1]", "if(len && str_buf[len-1]")
open(path, "w").write(text)
PYEOF
            rm -rf "$workdir"
            err "O patch de compatibilidade com kernels Clang falhou: o código do Linuwu-Sense mudou no upstream. Revise setup/install.sh."
            return 1
        }
    fi

    cp "$SRC_DIR/setup/dkms.conf" "$workdir/Linuwu-Sense/dkms.conf" || {
        rm -rf "$workdir"
        err "setup/dkms.conf não encontrado no nitroctl baixado."
        return 1
    }
    run_root rm -rf "$dkms_src"
    run_root cp -r "$workdir/Linuwu-Sense" "$dkms_src" || {
        rm -rf "$workdir"
        err "Não foi possível copiar a fonte para $dkms_src."
        return 1
    }
    rm -rf "$workdir"

    # Remove .ko manuais: o DKMS instala em updates/dkms e o depmod prefere
    # esse caminho; manter os dois geraria sombra silenciosa.
    for kdir in /usr/lib/modules/*/ /lib/modules/*/; do
        [ -d "$kdir" ] && run_root rm -f "${kdir}kernel/drivers/platform/x86/linuwu_sense.ko" 2>/dev/null
    done

    run_root dkms add -m "$DKMS_NAME" -v "$DKMS_VERSION" || {
        err "O dkms não aceitou o módulo. Veja 'dkms status'."
        return 1
    }
    run_root dkms autoinstall -m "$DKMS_NAME" -v "$DKMS_VERSION" || {
        err "A compilação via DKMS falhou. Veja /var/lib/dkms/${DKMS_NAME}/${DKMS_VERSION}/build/make.log."
        return 1
    }

    # Serviço + blacklist (vêm do repo, não do Linuwu-Sense): garantem que o
    # módulo DKMS carregue no boot e que o acer_wmi continue bloqueado.
    run_root cp "$SRC_DIR/setup/linuwu_sense.service" /etc/systemd/system/linuwu_sense.service
    run_root cp "$SRC_DIR/setup/blacklist-acer_wmi.conf" /etc/modprobe.d/blacklist-acer_wmi.conf
    run_root systemctl daemon-reload
    run_root systemctl enable linuwu_sense.service
    if ! run_root systemctl restart linuwu_sense.service; then
        err "O serviço não subiu com o módulo DKMS. Veja 'systemctl status linuwu_sense.service'."
        return 1
    fi
    msg "Driver registrado no DKMS e serviço ativado: o módulo recompila sozinho a cada kernel e carrega no boot."
}

uninstall_all() {
    if ! ask_yn "Remover o nitroctl ($SRC_DIR, links em $BIN_DIR) e o driver DKMS ($DKMS_NAME)?"; then
        err "Remoção cancelada."
        exit 1
    fi
    if [ "$OPT_DRY_RUN" -eq 1 ]; then
        printf '[dry-run] dkms remove, rm -rf %s, rm links em %s, modprobe acer_wmi\n' "/usr/src/${DKMS_NAME}-${DKMS_VERSION}" "$BIN_DIR" >&2
        return 0
    fi
    if command -v dkms >/dev/null 2>&1; then
        run_root dkms remove -m "$DKMS_NAME" -v "$DKMS_VERSION" --all 2>/dev/null || true
    fi
    run_root rm -rf "/usr/src/${DKMS_NAME}-${DKMS_VERSION}"
    run_root rm -f /etc/modprobe.d/blacklist-acer_wmi.conf
    run_root rm -f /etc/systemd/system/linuwu_sense.service
    run_root systemctl daemon-reload 2>/dev/null || true
    run_root modprobe acer_wmi 2>/dev/null || true
    rm -f "$BIN_DIR/nitroctl" "$BIN_DIR/nitroctl-gui"
    rm -rf "$SRC_DIR"
    msg "nitroctl e driver removidos. O driver original (acer_wmi) volta a ser usado após reiniciar."
}

check_path() {
    case ":$PATH:" in
        *":$BIN_DIR:"*) ;;
        *) msg "AVISO: $BIN_DIR não está no seu PATH.

Adicione ao final do seu ~/.profile (ou equivalente) e entre de novo na sessão:
export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
    esac
}

check_driver() {
    if [ -d /sys/devices/platform/acer-wmi ] || [ -d /sys/module/linuwu_sense ]; then
        return 0
    fi
    msg "AVISO: o driver Linuwu-Sense não foi encontrado neste sistema.

O nitroctl não controla o hardware sozinho: ele precisa do módulo Linuwu-Sense,
que a etapa DKMS deste instalador configura automaticamente."
}

main() {
    detect_ui
    resolve_profile || exit 1
    build_install_cmd
    log "install.sh v$VERSION | perfil=$P_ID pm=$P_PM sudo=$SUDO dry-run=$OPT_DRY_RUN"

    if [ "$OPT_UNINSTALL" -eq 1 ]; then uninstall_all; exit "$?"; fi
    if [ "$OPT_DRIVER_ONLY" -eq 1 ]; then install_driver_dkms; exit "$?"; fi

    if ! ask_yn "Bem-vindo ao instalador do nitroctl v$VERSION.

Perfil: $P_ID ($DISTRO_NAME)
Pacotes base: $P_BASE
GUI: ${P_GUI:-nenhuma}
DKMS: ${P_DKMS:-nenhum}

Continuar?"; then
        err "Instalação cancelada."
        exit 1
    fi

    install_base || exit 1
    if ! ask_yn "Baixar/atualizar o nitroctl em $SRC_DIR e criar os comandos em $BIN_DIR?

O programa será baixado da internet ($REPO_URL)."; then
        err "Instalação cancelada."
        exit 1
    fi
    install_nitroctl || exit 1
    install_gui_deps
    install_driver_dkms
    check_path
    check_driver

    msg "Instalação concluída.

Linha de comando:  nitroctl
Interface gráfica: nitroctl-gui (janela GTK4 nativa, eleva sozinha via polkit)"
}

main "$@"
