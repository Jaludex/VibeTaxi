"""
OptionsState for VibeTaxi.
Configures Master/Music/SFX/Engine/Ambience volumes, Fullscreen,
Gamepad Deadzone (with concentric circle visual), Show FPS, Physics Debug,
Pause on Focus Loss, and Language.
"""

from typing import Any, Callable, Optional
import pygame

import settings
from gale.state import BaseState
from gale.timer import Timer
from gale.ui.button import Button
from gale.ui.checkbox import Checkbox
from gale.ui.label import Label
from gale.ui.manager import UIManager
from gale.ui.panel import Panel

from src import audio, config, display
from src.gui.DeadzoneVisual import DeadzoneVisual
from src.gui.Slider import Slider
from src.gui.SpatialContainer import SpatialContainer
from src.i18n import tr
from src.menu_navigation import handle_menu_navigation
from src.themes import BUTTON_THEME, LABEL_THEME, PANEL_THEME


class OptionsState(BaseState):
    discord_presence = {"details": "Settings", "state": "Tuning options"}

    def __init__(self, state_machine: Any, on_close: Optional[Callable] = None) -> None:
        super().__init__(state_machine)
        self.on_close_callback = on_close
        self.fade_alpha: float = 0.0
        self.is_exiting: bool = False

        self.panel_width: int = 420
        self.panel_height: int = 230
        self.panel_x: float = (settings.VIRTUAL_WIDTH - self.panel_width) / 2
        self.panel_y: float = -260.0
        self.target_y: float = (settings.VIRTUAL_HEIGHT - self.panel_height) / 2
        self._last_panel_y: float = self.panel_y

        self.active_tab: str = "audio"  # "audio" or "game"

        self._build_ui()

    def _build_ui(self) -> None:
        from gale.ui.theme import Theme

        self.active_tab_theme = Theme(
            font=settings.FONTS["minecraft"],
            background_color=pygame.Color(160, 90, 130),
            hover_color=pygame.Color(180, 110, 150),
            focus_color=pygame.Color(255, 210, 60),
            text_color=pygame.Color(255, 255, 255),
            border_color=pygame.Color(255, 255, 255),
            border_width=2,
        )

        self.panel = Panel(
            self.panel_x,
            self.panel_y,
            self.panel_width,
            self.panel_height,
            theme=PANEL_THEME,
        )

        self.title_label = Label(
            settings.VIRTUAL_WIDTH / 2,
            self.panel_y + 10,
            tr("options_title"),
            theme=LABEL_THEME,
            center=True,
        )

        # Tab buttons
        self.btn_tab_audio = Button(
            self.panel_x + 30,
            self.panel_y + 26,
            90,
            20,
            tr("tab_audio"),
            on_click=lambda: self._set_tab("audio"),
            theme=self.active_tab_theme if self.active_tab == "audio" else BUTTON_THEME,
        )

        self.btn_tab_game = Button(
            self.panel_x + 130,
            self.panel_y + 26,
            110,
            20,
            tr("tab_game"),
            on_click=lambda: self._set_tab("game"),
            theme=self.active_tab_theme if self.active_tab == "game" else BUTTON_THEME,
        )

        # Bottom actions
        self.btn_reset = Button(
            self.panel_x + 25,
            self.panel_y + self.panel_height - 28,
            110,
            20,
            tr("btn_reset_defaults"),
            on_click=self._on_reset,
            theme=BUTTON_THEME,
        )

        self.btn_back = Button(
            self.panel_x + self.panel_width - 115,
            self.panel_y + self.panel_height - 28,
            90,
            20,
            tr("btn_back"),
            on_click=self._on_back,
            theme=BUTTON_THEME,
        )

        # --- TAB: AUDIO CONTROLS ---
        slider_w = 170
        slider_h = 16
        col_lbl_x = self.panel_x + 30
        col_val_x = self.panel_x + 160

        y_off = 54
        dy = 24

        self.lbl_master = Label(col_lbl_x, self.panel_y + y_off, tr("opt_master"), theme=LABEL_THEME)
        self.sld_master = Slider(
            col_val_x, self.panel_y + y_off - 2, slider_w, slider_h,
            value=config.get("master_volume", 1.0),
            on_change=lambda val: self._on_volume_change("master_volume", val, "master"),
        )

        self.lbl_music = Label(col_lbl_x, self.panel_y + y_off + dy, tr("opt_music"), theme=LABEL_THEME)
        self.sld_music = Slider(
            col_val_x, self.panel_y + y_off + dy - 2, slider_w, slider_h,
            value=config.get("music_volume", 0.8),
            on_change=lambda val: self._on_volume_change("music_volume", val, "music"),
        )

        self.lbl_sfx = Label(col_lbl_x, self.panel_y + y_off + dy * 2, tr("opt_sfx"), theme=LABEL_THEME)
        self.sld_sfx = Slider(
            col_val_x, self.panel_y + y_off + dy * 2 - 2, slider_w, slider_h,
            value=config.get("sfx_volume", 1.0),
            on_change=lambda val: self._on_volume_change("sfx_volume", val, "sfx"),
        )

        self.lbl_engine = Label(col_lbl_x, self.panel_y + y_off + dy * 3, tr("opt_engine"), theme=LABEL_THEME)
        self.sld_engine = Slider(
            col_val_x, self.panel_y + y_off + dy * 3 - 2, slider_w, slider_h,
            value=config.get("engine_volume", 1.0),
            on_change=lambda val: self._on_volume_change("engine_volume", val, "engine"),
        )

        self.lbl_ambient = Label(col_lbl_x, self.panel_y + y_off + dy * 4, tr("opt_ambient"), theme=LABEL_THEME)
        self.sld_ambient = Slider(
            col_val_x, self.panel_y + y_off + dy * 4 - 2, slider_w, slider_h,
            value=config.get("ambient_volume", 1.0),
            on_change=lambda val: self._on_volume_change("ambient_volume", val, "ambient"),
        )

        self.audio_widgets = [
            self.lbl_master, self.sld_master,
            self.lbl_music, self.sld_music,
            self.lbl_sfx, self.sld_sfx,
            self.lbl_engine, self.sld_engine,
            self.lbl_ambient, self.sld_ambient,
        ]

        # --- TAB: GAME CONTROLS ---
        g_y_off = 52
        g_dy = 22

        # Fullscreen
        self.chk_fullscreen = Checkbox(
            col_lbl_x, self.panel_y + g_y_off, 15,
            checked=display.is_fullscreen(),
            on_change=self._on_fullscreen_toggle,
        )
        self.lbl_fullscreen = Label(col_lbl_x + 22, self.panel_y + g_y_off, tr("opt_fullscreen"), theme=LABEL_THEME)

        # Gamepad Deadzone
        deadzone_val = float(config.get("gamepad_deadzone", 0.25))
        self.lbl_deadzone = Label(col_lbl_x, self.panel_y + g_y_off + g_dy, tr("opt_deadzone"), theme=LABEL_THEME)
        self.sld_deadzone = Slider(
            col_val_x - 30, self.panel_y + g_y_off + g_dy - 2, 140, slider_h,
            value=deadzone_val,
            min_val=0.05, max_val=0.50, step=0.01,
            format_str="{:.0%}",
            on_change=self._on_deadzone_change,
        )
        self.vis_deadzone = DeadzoneVisual(
            self.panel_x + self.panel_width - 80,
            self.panel_y + g_y_off + g_dy - 12,
            size=44,
            deadzone=deadzone_val,
        )

        # Show FPS
        self.chk_fps = Checkbox(
            col_lbl_x, self.panel_y + g_y_off + g_dy * 2 + 10, 15,
            checked=bool(config.get("show_fps", False)),
            on_change=lambda val: config.set("show_fps", val),
        )
        self.lbl_fps = Label(col_lbl_x + 22, self.panel_y + g_y_off + g_dy * 2 + 10, tr("opt_show_fps"), theme=LABEL_THEME)

        # Physics Debug
        self.chk_debug = Checkbox(
            col_lbl_x, self.panel_y + g_y_off + g_dy * 3 + 10, 15,
            checked=bool(config.get("physics_debug", False)),
            on_change=lambda val: config.set("physics_debug", val),
        )
        self.lbl_debug = Label(col_lbl_x + 22, self.panel_y + g_y_off + g_dy * 3 + 10, tr("opt_debug_visuals"), theme=LABEL_THEME)

        # Pause on Focus Loss
        self.chk_focus = Checkbox(
            col_lbl_x, self.panel_y + g_y_off + g_dy * 4 + 10, 15,
            checked=bool(config.get("pause_on_focus_loss", True)),
            on_change=lambda val: config.set("pause_on_focus_loss", val),
        )
        self.lbl_focus = Label(col_lbl_x + 22, self.panel_y + g_y_off + g_dy * 4 + 10, tr("opt_pause_on_focus_loss"), theme=LABEL_THEME)

        # Discord RPC
        col_right_x = self.panel_x + self.panel_width - 150
        self.chk_discord = Checkbox(
            col_right_x, self.panel_y + g_y_off + g_dy * 2 + 10, 15,
            checked=bool(config.get("discord_rpc", True)),
            on_change=self._on_discord_toggle,
        )
        self.lbl_discord = Label(col_right_x + 22, self.panel_y + g_y_off + g_dy * 2 + 10, tr("opt_discord_rpc"), theme=LABEL_THEME)

        # Language button
        lang_code = config.get("language") or getattr(settings, "LANGUAGE", "es") or "es"
        lang_name = tr("language_name", default=lang_code.upper())
        self.btn_language = Button(
            self.panel_x + self.panel_width - 150,
            self.panel_y + g_y_off + g_dy * 3 + 6,
            120,
            24,
            f"{tr('btn_language')}: {lang_name}",
            on_click=self._on_language_click,
            theme=BUTTON_THEME,
        )

        # FPS Limit button
        self.btn_fps = Button(
            self.panel_x + self.panel_width - 150,
            self.panel_y + g_y_off + g_dy * 4 + 6,
            120,
            24,
            self._get_fps_button_text(),
            on_click=self._on_fps_click,
            theme=BUTTON_THEME,
        )

        self.game_widgets = [
            self.chk_fullscreen, self.lbl_fullscreen,
            self.lbl_deadzone, self.sld_deadzone, self.vis_deadzone,
            self.chk_fps, self.lbl_fps,
            self.chk_debug, self.lbl_debug,
            self.chk_focus, self.lbl_focus,
            self.chk_discord, self.lbl_discord,
            self.btn_language,
            self.btn_fps,
        ]

        self.container = SpatialContainer(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.ui = UIManager(
            self.container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT,
        )

        self._refresh_container_children()

    def _refresh_container_children(self) -> None:
        self.container.children.clear()
        self.container.add_child(self.panel)
        self.container.add_child(self.title_label)
        self.container.add_child(self.btn_tab_audio)
        self.container.add_child(self.btn_tab_game)

        tab_list = self.audio_widgets if self.active_tab == "audio" else self.game_widgets
        for w in tab_list:
            self.container.add_child(w)

        self.container.add_child(self.btn_reset)
        self.container.add_child(self.btn_back)

    def _set_tab(self, tab: str) -> None:
        if self.active_tab == tab:
            return
        audio.play_sfx("press")
        self.active_tab = tab
        self.btn_tab_audio.theme = self.active_tab_theme if tab == "audio" else BUTTON_THEME
        self.btn_tab_game.theme = self.active_tab_theme if tab == "game" else BUTTON_THEME
        self._refresh_container_children()

    def _on_volume_change(self, key: str, value: float, category: str) -> None:
        config.set(key, value)
        audio.play_preview(category)

    def _on_deadzone_change(self, val: float) -> None:
        config.set("gamepad_deadzone", val)
        self.vis_deadzone.set_deadzone(val)

    def _on_discord_toggle(self, checked: bool) -> None:
        audio.play_sfx("press")
        config.set("discord_rpc", checked)
        import sys
        main_module = sys.modules.get("__main__")
        game = getattr(main_module, "game", None)
        if game and hasattr(game, "discord_rpc"):
            game.discord_rpc.set_enabled(checked)

    def _on_fullscreen_toggle(self, checked: bool) -> None:
        audio.play_sfx("press")
        display.set_fullscreen(checked)

    def _on_language_click(self) -> None:
        audio.play_sfx("press")
        from src.states.game.Menus.LanguageSelectionState import LanguageSelectionState
        self.state_machine.push(LanguageSelectionState(self.state_machine, on_close=self._on_language_changed))

    def _on_language_changed(self) -> None:
        self._build_ui()
        self.update_ui_y()

    def _get_fps_button_text(self) -> str:
        val = config.get("fps_limit", 60)
        label = tr("opt_fps_limit", default="FPS")
        if val == "auto":
            hz = display.get_monitor_refresh_rate()
            return f"{label}: {tr('fps_auto')} ({hz}Hz)"
        elif val == 0 or val == "0" or val == "unlimited":
            return f"{label}: {tr('fps_uncapped')}"
        else:
            return f"{label}: {val}"

    def _on_fps_click(self) -> None:
        audio.play_sfx("press")
        choices = [30, 60, 90, 120, 144, "auto", 0]
        current = config.get("fps_limit", 60)
        if current not in choices:
            try:
                current = int(current)
                if current not in choices:
                    current = 60
            except Exception:
                current = 60
        idx = choices.index(current)
        next_val = choices[(idx + 1) % len(choices)]

        config.set("fps_limit", next_val, auto_save=True)
        import sys
        main_module = sys.modules.get("__main__")
        game = getattr(main_module, "game", None)
        if game and hasattr(game, "set_fps_limit"):
            game.set_fps_limit(next_val, save=True)

        self.btn_fps.text = self._get_fps_button_text()

    def _on_reset(self) -> None:
        audio.play_sfx("press")
        config.reset_defaults()
        # Update Audio sliders
        self.sld_master.set_value(config.get("master_volume", 1.0), notify=False)
        self.sld_music.set_value(config.get("music_volume", 0.8), notify=False)
        self.sld_sfx.set_value(config.get("sfx_volume", 1.0), notify=False)
        self.sld_engine.set_value(config.get("engine_volume", 1.0), notify=False)
        self.sld_ambient.set_value(config.get("ambient_volume", 1.0), notify=False)
        audio.refresh_music()

        # Update Game widgets
        self.chk_fullscreen.checked = False
        display.set_fullscreen(False)
        dz = float(config.get("gamepad_deadzone", 0.25))
        self.sld_deadzone.set_value(dz, notify=False)
        self.vis_deadzone.set_deadzone(dz)
        self.chk_fps.checked = bool(config.get("show_fps", False))
        self.chk_debug.checked = bool(config.get("physics_debug", False))
        self.chk_focus.checked = bool(config.get("pause_on_focus_loss", True))
        self.chk_discord.checked = bool(config.get("discord_rpc", True))
        self.btn_fps.text = self._get_fps_button_text()
        import sys
        main_module = sys.modules.get("__main__")
        game = getattr(main_module, "game", None)
        if game and hasattr(game, "discord_rpc"):
            game.discord_rpc.set_enabled(True)
        if game and hasattr(game, "set_fps_limit"):
            game.set_fps_limit(60, save=True)

    def enter(self, enter_params: Optional[dict] = None) -> None:
        self.fade_alpha = 0.0
        self.panel_y = -260.0
        self.is_exiting = False
        self.update_ui_y()

        Timer.tween(
            0.35,
            [(self, {"fade_alpha": 180.0, "panel_y": self.target_y})],
            ease_function_name="out_cubic",
        )

    def update_ui_y(self) -> None:
        dy = self.panel_y - self._last_panel_y
        if dy != 0:
            for child in self.container.children:
                child.y += dy
            # Keep widgets not currently in container updated as well
            other_widgets = self.game_widgets if self.active_tab == "audio" else self.audio_widgets
            for w in other_widgets:
                w.y += dy
            self._last_panel_y = self.panel_y

    def update(self, dt: float) -> None:
        self.update_ui_y()
        # Keep fullscreen checkbox synced with physical display (e.g. F11 pressed)
        if self.chk_fullscreen.checked != display.is_fullscreen():
            self.chk_fullscreen.checked = display.is_fullscreen()

    def render(self, surface: pygame.Surface) -> None:
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
            )
            fade_surface.fill((0, 0, 0, int(self.fade_alpha)))
            surface.blit(fade_surface, (0, 0))

        self.ui.render(surface)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if self.is_exiting:
            return

        if input_id == "pause" and getattr(input_data, "pressed", False):
            self._on_back()
            return

        handled = handle_menu_navigation(self.ui, input_id, input_data)
        if not handled:
            self.ui.on_input(input_id, input_data)

    def _on_back(self) -> None:
        if self.is_exiting:
            return
        audio.play_sfx("press")
        self.is_exiting = True
        config.save()

        Timer.tween(
            0.3,
            [(self, {"fade_alpha": 0.0, "panel_y": -280.0})],
            ease_function_name="in_cubic",
            on_finish=self._close,
        )

    def _close(self) -> None:
        self.state_machine.pop()
        if self.on_close_callback:
            self.on_close_callback()
