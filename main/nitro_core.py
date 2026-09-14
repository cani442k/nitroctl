#!/usr/bin/env python3
"""Camada de acesso ao driver Linuwu-Sense, compartilhada pelo CLI e pela GUI.

Toda leitura e escrita no sysfs fica concentrada aqui para que main.py (CLI) e
gtk_app.py (GTK4) não dupliquem caminhos nem regras de validação.
"""
from __future__ import annotations

import os
import pwd
import sys
from pathlib import Path

MODULE_NAME = "linuwu_sense"

# O driver expõe os atributos do modelo em um destes dois pontos de montagem,
# a depender de como o módulo foi carregado.
SENSE_BASES = (
    Path(f"/sys/module/{MODULE_NAME}/drivers/platform:acer-wmi/acer-wmi"),
    Path("/sys/devices/platform/acer-wmi"),
)
MODEL_DIRS = ("nitro_sense", "predator_sense")

PLATFORM_PROFILE = Path("/sys/firmware/acpi/platform_profile")
PLATFORM_PROFILE_CHOICES = Path("/sys/firmware/acpi/platform_profile_choices")

PROFILE_LABELS = {
    "balanced-performance": "Performance",
    "performance": "Turbo",
    "low-power": "Eco",
    "balanced": "Balanced",
    "quiet": "Quiet",
}

FAN_AUTO = 0
FAN_MIN = 1
FAN_MAX = 100

# Atributos de liga/desliga expostos pela interface do CLI.
FLAG_ATTRS = ("backlight_timeout", "battery_limiter", "lcd_override")


class DriverMissing(RuntimeError):
    """O driver Linuwu-Sense não está instalado ou não expõe a interface."""


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def is_root() -> bool:
    return os.geteuid() == 0


def driver_base() -> Path | None:
    """Diretório do driver que contém uma subpasta de modelo, se houver."""
    for base in SENSE_BASES:
        for model in MODEL_DIRS:
            if (base / model).is_dir():
                return base
    return None


def sense_dir() -> Path:
    base = driver_base()
    if base is None:
        raise DriverMissing(
            f"Driver Linuwu-Sense não encontrado em {SENSE_BASES[0]} nem em {SENSE_BASES[1]}. "
            "Instale o driver antes de usar o nitroctl."
        )
    for model in MODEL_DIRS:
        candidate = base / model
        if candidate.is_dir():
            return candidate
    raise DriverMissing("Diretório do modelo não encontrado.")


def model_name() -> str:
    try:
        return sense_dir().name
    except DriverMissing:
        return ""


def supports(attr: str) -> bool:
    """Indica se o modelo atual expõe determinado atributo."""
    try:
        return (sense_dir() / attr).is_file()
    except DriverMissing:
        return False


def features() -> list[str]:
    try:
        return sorted(item.name for item in sense_dir().iterdir() if item.is_file())
    except (DriverMissing, OSError):
        return []


def read_attr(attr: str) -> str:
    path = sense_dir() / attr
    return path.read_text().strip()


def read_attr_or_none(attr: str) -> str | None:
    try:
        return read_attr(attr)
    except (DriverMissing, OSError):
        return None


def write_attr(attr: str, value) -> None:
    """Escreve um valor no sysfs. Propaga OSError/PermissionError para quem chama."""
    (sense_dir() / attr).write_text(f"{value}")


def read_flag(attr: str) -> bool | None:
    """Lê um atributo 0/1. Devolve None quando ausente ou com valor inesperado."""
    raw = read_attr_or_none(attr)
    if raw in ("0", "1"):
        return raw == "1"
    return None


def set_flag(attr: str, enabled: bool) -> None:
    write_attr(attr, 1 if enabled else 0)


def thermal_profiles() -> list[tuple[str, str]]:
    """Pares (valor do kernel, rótulo de exibição) na ordem informada pelo firmware."""
    raw = PLATFORM_PROFILE_CHOICES.read_text().split()
    return [(mode, PROFILE_LABELS.get(mode, mode)) for mode in raw]


def current_thermal_profile() -> str | None:
    try:
        return PLATFORM_PROFILE.read_text().strip()
    except OSError:
        return None


def set_thermal_profile(raw_mode: str) -> None:
    if raw_mode not in [mode for mode, _ in thermal_profiles()]:
        raise ValueError(f"Perfil térmico inválido: {raw_mode}")
    PLATFORM_PROFILE.write_text(f"{raw_mode}\n")


def fan_speed() -> tuple[int, int] | None:
    """Velocidades atuais (cpu, gpu); 0 significa controle automático."""
    raw = read_attr_or_none("fan_speed")
    if not raw:
        return None
    parts = [part.strip() for part in raw.split(",")]
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        return None
    return int(parts[0]), int(parts[1])


def valid_fan_speed(speed) -> bool:
    try:
        speed = int(speed)
    except (TypeError, ValueError):
        return False
    return speed == FAN_AUTO or FAN_MIN <= speed <= FAN_MAX


def set_fan_speed(cpu: int, gpu: int) -> None:
    cpu, gpu = int(cpu), int(gpu)
    if not valid_fan_speed(cpu) or not valid_fan_speed(gpu):
        raise ValueError(f"Velocidade fora da faixa permitida (0 = automático, {FAN_MIN}-{FAN_MAX}).")
    write_attr("fan_speed", f"{cpu},{gpu}")


def user_home() -> Path:
    """Home do usuário real, mesmo quando o programa roda via sudo."""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            return Path(f"/home/{sudo_user}")
    return Path.home()


def config_dir() -> Path:
    return user_home() / ".config" / "nitroctl"


def save_config() -> tuple[list[str], list[tuple[str, str]]]:
    """Copia os atributos atuais para ~/.config/nitroctl.

    Devolve (salvos, pulados), em que pulados são pares (nome, motivo).
    """
    target_dir = config_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    skipped: list[tuple[str, str]] = []
    for item in sorted(sense_dir().iterdir()):
        if not item.is_file():
            continue
        try:
            (target_dir / item.name).write_text(item.read_text().strip())
            saved.append(item.name)
        except OSError as exc:
            skipped.append((item.name, str(exc)))
    return saved, skipped


def load_config() -> tuple[list[str], list[tuple[str, str]]]:
    """Reaplica em sysfs os valores guardados em ~/.config/nitroctl.

    Devolve (aplicados, pulados). Não há verificação de compatibilidade: o
    próprio projeto marca esta função como não testada.
    """
    source_dir = config_dir()
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Nenhuma configuração salva em {source_dir}")
    applied: list[str] = []
    skipped: list[tuple[str, str]] = []
    for item in sorted(source_dir.iterdir()):
        if not item.is_file():
            continue
        try:
            (sense_dir() / item.name).write_text(item.read_text().strip())
            applied.append(item.name)
        except OSError as exc:
            skipped.append((item.name, str(exc)))
    return applied, skipped