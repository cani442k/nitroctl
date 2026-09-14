#!/usr/bin/env python3
"""Interface gráfica nativa do nitroctl (GTK4 + Libadwaita).

Cobre as mesmas funções do CLI (main.py): perfil térmico, velocidade das
ventoinhas, limitador de bateria, timeout do RGB do teclado, LCD Overdrive
e salvar/carregar configuração.

Precisa rodar como root para escrever no sysfs do driver Linuwu-Sense; quando
aberto sem privilégios, a janela mostra o estado em modo somente leitura e
oferece um botão de elevação via pkexec. Imagens e escrita vão sempre pelo
módulo compartilhado nitro_core, o mesmo usado pelo CLI.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk  # noqa: E402

import nitro_core as core

APP_ID = "io.github.cani442k.nitroctl"


def fan_text(speed: int) -> str:
    return "Auto" if speed == core.FAN_AUTO else f"{speed}%"


class NitroWindow(Adw.ApplicationWindow):
    """Janela principal: lê o estado do driver e liga cada controle ao core."""

    def __init__(self, app: Adw.Application):
        super().__init__(application=app)
        self.set_title("nitroctl")
        self.set_default_size(560, 720)

        self.can_write = core.is_root()

        # Adw.ApplicationWindow não aceita set_titlebar: o header vai dentro
        # de um Adw.ToolbarView, que é o content da janela.
        header = Adw.HeaderBar()
        refresh = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        refresh.set_tooltip_text("Reload state from the driver")
        refresh.connect("clicked", lambda _button: self.refresh())
        header.pack_end(refresh)

        self.toast_overlay = Adw.ToastOverlay()

        # Respiro entre a janela e o conteúdo (fora) + entre os cartões (dentro).
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        page.set_margin_top(24)
        page.set_margin_bottom(24)
        page.set_margin_start(24)
        page.set_margin_end(24)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(page)
        scrolled.set_vexpand(True)
        self.toast_overlay.set_child(scrolled)

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(self.toast_overlay)
        self.set_content(toolbar_view)

        if not self.can_write:
            banner = Adw.Banner.new(
                "Read-only: restart with 'nitroctl-gui' (it asks for your "
                "password) to apply changes."
            )
            banner.set_revealed(True)
            page.append(banner)

        self.profile_group = self._build_profile_group()
        page.append(self.profile_group)

        self.fan_group = self._build_fan_group()
        page.append(self.fan_group)

        self.toggle_group = self._build_toggle_group()
        page.append(self.toggle_group)

        self.config_group = self._build_config_group()
        page.append(self.config_group)

        self.status_label = Gtk.Label()
        self.status_label.set_wrap(True)
        self.status_label.add_css_class("dim-label")
        self.status_label.set_margin_top(12)
        page.append(self.status_label)

        self.refresh()

    # ------------------------------------------------------------ construção
    def _locked_note(self, row: Adw.ActionRow, attr: str) -> None:
        row.set_subtitle(f"This device does not expose '{attr}'. Unavailable.")

    def _build_profile_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup()
        group.set_title("Thermal profile")
        group.set_description("Power profiles exposed by the firmware (ACPI platform_profile).")

        self.profile_model = Gtk.StringList()
        self.profile_combo = Adw.ComboRow()
        self.profile_combo.set_title("Profile")
        self.profile_combo.set_model(self.profile_model)
        self.profile_combo.set_sensitive(self.can_write)
        self.profile_combo.connect("notify::selected", self._on_profile_selected)
        self._profile_updating = False
        group.add(self.profile_combo)
        # Margem interna do cartão de perfil (o ComboRow é o único filho).
        self.profile_combo.set_margin_top(12)
        self.profile_combo.set_margin_bottom(12)
        self.profile_combo.set_margin_start(12)
        self.profile_combo.set_margin_end(12)
        return group

    def _build_fan_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup()
        group.set_title("Fan speed")
        group.set_description("Auto hands control back to the firmware; 1-100 forces a fixed speed.")

        self.fan_rows: dict[str, tuple[Adw.SwitchRow, Adw.SpinRow]] = {}
        for device in ("CPU", "GPU"):
            auto = Adw.SwitchRow()
            auto.set_title(f"{device} automatic")
            auto.set_sensitive(self.can_write)
            auto.connect("notify::active", self._on_fan_auto_toggled, device)
            group.add(auto)
            speed = Adw.SpinRow()
            speed.set_title(f"{device} speed")
            speed.set_subtitle("Percent, 1-100")
            speed.set_adjustment(Gtk.Adjustment(value=50, lower=1, upper=100, step_increment=1, page_increment=10))
            speed.set_sensitive(False)
            group.add(speed)
            self.fan_rows[device] = (auto, speed)

        apply_button = Gtk.Button.new_with_label("Apply fan speeds")
        apply_button.add_css_class("suggested-action")
        apply_button.set_sensitive(self.can_write)
        apply_button.connect("clicked", self._on_apply_fan_speed)
        # O botão de ação fica fora do cartão, com respiro acima.
        apply_button.set_margin_top(12)
        page_button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_button_box.append(apply_button)
        group.add(page_button_box)
        return group

    def _build_toggle_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup()
        group.set_title("Power and display")
        group.set_description("Applied immediately when toggled.")

        self.toggle_rows: dict[str, Adw.SwitchRow] = {}
        for attr, title, subtitle in (
            ("battery_limiter", "Battery limiter", "Limits the maximum charge level."),
            ("backlight_timeout", "Keyboard RGB timeout", "Turns the keyboard backlight off after idle."),
            ("lcd_override", "LCD Overdrive", "Faster LCD response time."),
        ):
            row = Adw.SwitchRow()
            row.set_title(title)
            row.connect("notify::active", self._on_flag_toggled, attr)
            group.add(row)
            row.set_subtitle(subtitle)
            self.toggle_rows[attr] = row
        return group

    def _build_config_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup()
        group.set_title("Configuration")
        group.set_description(f"Files saved in {core.config_dir()}")

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        buttons.set_margin_top(12)
        save_button = Gtk.Button.new_with_label("Save configuration")
        save_button.add_css_class("suggested-action")
        save_button.set_sensitive(self.can_write)
        save_button.connect("clicked", self._on_save_config)
        load_button = Gtk.Button.new_with_label("Load configuration")
        load_button.set_sensitive(self.can_write)
        load_button.connect("clicked", self._on_ask_load_config)
        buttons.append(save_button)
        buttons.append(load_button)
        group.add(buttons)
        return group

    # ---------------------------------------------------------------- estado
    def refresh(self) -> None:
        try:
            profiles = core.thermal_profiles()
        except OSError:
            profiles = []
        self._profile_updating = True
        try:
            self.profile_model.splice(0, self.profile_model.get_n_items(), [label for _, label in profiles])
            current = core.current_thermal_profile()
            keys = [mode for mode, _ in profiles]
            if current in keys:
                self.profile_combo.set_selected(keys.index(current))
            else:
                self.profile_combo.set_selected(Gtk.INVALID_LIST_POSITION)
            self.profile_combo.set_sensitive(self.can_write and bool(profiles))
        finally:
            self._profile_updating = False

        speeds = core.fan_speed() or (core.FAN_AUTO, core.FAN_AUTO)
        for device, speed in zip(("CPU", "GPU"), speeds):
            auto_row, speed_row = self.fan_rows[device]
            auto = speed == core.FAN_AUTO
            auto_row.handler_block_by_func(self._on_fan_auto_toggled)
            auto_row.set_active(auto)
            auto_row.handler_unblock_by_func(self._on_fan_auto_toggled)
            if not auto:
                speed_row.set_value(speed)
            speed_row.set_sensitive(self.can_write and not auto)
            auto_row.set_sensitive(self.can_write)

        for attr, row in self.toggle_rows.items():
            row.handler_block_by_func(self._on_flag_toggled)
            try:
                if not core.supports(attr):
                    row.set_active(False)
                    row.set_sensitive(False)
                    self._locked_note(row, attr)
                else:
                    row.set_active(bool(core.read_flag(attr)))
                    row.set_sensitive(self.can_write)
            finally:
                row.handler_unblock_by_func(self._on_flag_toggled)

        try:
            model = core.model_name()
            attrs = ", ".join(core.features()) or "none"
            base = core.driver_base()
            interface = f"Interface: {base}/{model}\nDriver attributes: {attrs}"
        except core.DriverMissing as exc:
            interface = str(exc)
        self.status_label.set_text(
            f"{interface}\nKeyboard RGB: not implemented by the upstream project."
        )

    # ----------------------------------------------------------------- ações
    def notify(self, message: str, error: bool = False) -> None:
        toast = Adw.Toast.new(message)
        if error:
            toast.set_priority(Adw.ToastPriority.HIGH)
        self.toast_overlay.add_toast(toast)

    @staticmethod
    def _fail_message(exc: Exception) -> str:
        if isinstance(exc, PermissionError):
            return "Permission denied. Run nitroctl with sudo."
        if isinstance(exc, core.DriverMissing):
            return str(exc)
        return f"Failed: {exc}"

    def _on_profile_selected(self, combo: Adw.ComboRow, _param: object) -> None:
        if self._profile_updating or not self.can_write:
            return
        try:
            profiles = core.thermal_profiles()
        except OSError as exc:
            self.notify(self._fail_message(exc), error=True)
            self.refresh()
            return
        selected = combo.get_selected()
        if selected == Gtk.INVALID_LIST_POSITION or selected >= len(profiles):
            return
        mode, label = profiles[selected]
        try:
            core.set_thermal_profile(mode)
            self.notify(f"Thermal profile: {label}")
        except (OSError, ValueError) as exc:
            self.notify(self._fail_message(exc), error=True)
        self.refresh()

    def _on_fan_auto_toggled(self, row: Adw.SwitchRow, _param: object, device: str) -> None:
        _auto_row, speed_row = self.fan_rows[device]
        speed_row.set_sensitive(self.can_write and not row.get_active())

    def _on_apply_fan_speed(self, _button: Gtk.Button) -> None:
        values = {}
        for device, (auto_row, speed_row) in self.fan_rows.items():
            values[device] = core.FAN_AUTO if auto_row.get_active() else int(speed_row.get_value())
        try:
            core.set_fan_speed(values["CPU"], values["GPU"])
            self.notify(f"Fans: CPU {fan_text(values['CPU'])}, GPU {fan_text(values['GPU'])}")
        except (OSError, ValueError) as exc:
            self.notify(self._fail_message(exc), error=True)
        self.refresh()

    def _on_flag_toggled(self, row: Adw.SwitchRow, _param: object, attr: str) -> None:
        try:
            core.set_flag(attr, row.get_active())
            self.notify(f"{row.get_title()}: {'on' if row.get_active() else 'off'}")
        except (OSError, ValueError) as exc:
            self.notify(self._fail_message(exc), error=True)
        self.refresh()

    def _on_save_config(self, _button: Gtk.Button) -> None:
        try:
            saved, skipped = core.save_config()
            note = f"{len(saved)} values saved"
            if skipped:
                note += f", {len(skipped)} skipped"
            self.notify(note)
        except OSError as exc:
            self.notify(self._fail_message(exc), error=True)

    def _on_ask_load_config(self, _button: Gtk.Button) -> None:
        dialog = Adw.AlertDialog()
        dialog.set_heading("Load saved configuration?")
        dialog.set_body(
            "The upstream project marks this feature as untested and warns that it may "
            "break your system. The saved values are written straight to the driver."
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("load", "Load")
        dialog.set_response_appearance("load", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.choose(self, None, self._on_load_confirmed)

    def _on_load_confirmed(self, dialog: Adw.AlertDialog, result: Gio.AsyncResult) -> None:
        if dialog.choose_finish(result) != "load":
            return
        try:
            applied, skipped = core.load_config()
            note = f"{len(applied)} values applied"
            if skipped:
                note += f", {len(skipped)} skipped"
            self.notify(note)
        except OSError as exc:
            self.notify(self._fail_message(exc), error=True)
        self.refresh()


class NitroApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

    def do_activate(self) -> None:
        window = self.props.active_window or NitroWindow(self)
        window.present()


def ensure_root() -> None:
    """Reexecuta via pkexec quando aberto como usuário comum.

    Passa --no-elevate para a cópia elevada não tentar se elevar de novo
    (evitaria um loop caso o pkexec não eleve de fato). Também fixa SHELL
    para um valor presente em /etc/shells, porque o pkexec reclama quando
    o shell do usuário não está listado lá, e repassa o display Wayland/X11
    para o root — sem isso o app elevado não encontra o display e o Gtk
    falha com "couldn't be initialized".
    """
    if core.is_root():
        return
    script = Path(__file__).resolve()
    try:
        env = dict(os.environ, SHELL="/bin/sh")
        keep = ("DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR",
                "XDG_SESSION_TYPE", "DBUS_SESSION_BUS_ADDRESS")
        preserved = [f"{key}={env[key]}" for key in keep if env.get(key)]
        subprocess.run(
            ["pkexec", "env", f"SHELL={env['SHELL']}", *preserved,
             sys.executable or "python3", str(script),
             "--no-elevate", *sys.argv[1:]],
            check=False,
            env=env,
        )
    except FileNotFoundError:
        print(f"pkexec not found; rerun as root: sudo python3 {script}", file=sys.stderr)
    sys.exit(0)


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--no-elevate" not in args:
        ensure_root()
    args = [a for a in args if a != "--no-elevate"]
    app = NitroApp()
    return app.run([sys.argv[0], *args])


if __name__ == "__main__":
    sys.exit(main())
