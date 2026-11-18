from __future__ import annotations

import pygame
from typing import Any

from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateStack

from src.states.game.Menus.OpeningState import OpeningState


class VibeStateStack(StateStack):
    def render(self, surface: pygame.Surface) -> None:
        start_idx = 0
        for i in range(len(self.states) - 1, -1, -1):
            st = self.states[i]
            if getattr(st, "opaque", False) or type(st).__name__ in ("PlayState", "TutorialPlayState", "TitleScreenState"):
                start_idx = i
                break
        for st in self.states[start_idx:]:
            st.render(surface)


class VibeTaxi(Game):
    def __init__(self, *args, **kwargs):
        import settings
        import gale.game
        import gale.log
        from src.os_tools import is_android
        import os

        # Setup gale.log early
        log_dir = os.environ.get("ANDROID_PRIVATE", ".")
        log_file = os.path.join(log_dir, "vibetaxi.log")
        try:
            gale.log.configure(level=gale.log.LogLevel.INFO, log_file=log_file, console=True)
        except Exception:
            pass
        self.logger = gale.log.get_logger("engine")

        # Ensure gale.game.INPUT_EVENTS handles touch events on Android
        gale.game.INPUT_EVENTS = gale.game.INPUT_EVENTS + (
            pygame.FINGERDOWN,
            pygame.FINGERUP,
            pygame.FINGERMOTION,
        )

        if not is_android():
            icon = settings.TEXTURES.get("game_icon")
            if icon:
                try:
                    pygame.display.set_icon(icon)
                except Exception:
                    pass

        if is_android():
            kwargs.setdefault("window_width", settings.VIRTUAL_WIDTH)
            kwargs.setdefault("window_height", settings.VIRTUAL_HEIGHT)
            kwargs.setdefault("virtual_width", settings.VIRTUAL_WIDTH)
            kwargs.setdefault("virtual_height", settings.VIRTUAL_HEIGHT)
            try:
                kwargs["flags"] = pygame.SCALED | pygame.FULLSCREEN
                super().__init__(*args, **kwargs)
            except Exception as e:
                print(f"Warning: SCALED | FULLSCREEN failed ({e}), falling back to FULLSCREEN")
                kwargs["flags"] = pygame.FULLSCREEN
                super().__init__(*args, **kwargs)
        else:
            kwargs.setdefault("flags", pygame.SCALED | pygame.RESIZABLE)
            super().__init__(*args, **kwargs)

        if hasattr(self, "screen") and self.screen:
            settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT = self.screen.get_size()
            # Convert all loaded textures to the display format for fast blitting
            for tex_name, tex_surf in list(settings.TEXTURES.items()):
                if isinstance(tex_surf, pygame.Surface):
                    try:
                        if tex_surf.get_flags() & pygame.SRCALPHA:
                            settings.TEXTURES[tex_name] = tex_surf.convert_alpha()
                        else:
                            settings.TEXTURES[tex_name] = tex_surf.convert()
                    except Exception:
                        pass
        self.is_fullscreen: bool = is_android()

        self.logger.info(f"BOOT: screen_size={self.screen.get_size()} flags={self.screen.get_flags()} virt={(self.virtual_width, self.virtual_height)}")

    def init(self) -> None:
        global pygame
        from gale.ui.theme import set_default_theme
        from gale.input_handler import InputHandler
        from gale.ui.manager import UIManager
        from src.mouse_tools import physical_to_virtual
        from src.themes import DEFAULT_THEME
        set_default_theme(DEFAULT_THEME)

        # Patch UIManager coordinate rescaling to dynamically adapt to actual screen and aspect ratio
        UIManager._rescale = lambda ui_self, pos: physical_to_virtual(pos[0], pos[1])

        # Optimize Gale Button rendering to cache Text rasterization
        from gale.ui.button import Button
        def cached_btn_render(btn_self, surface: pygame.Surface) -> None:
            if not btn_self.visible:
                return

            if btn_self.focused:
                fill_color = btn_self.theme.focus_color
            elif btn_self.hovered and btn_self.enabled:
                fill_color = btn_self.theme.hover_color
            else:
                fill_color = btn_self.theme.background_color

            pygame.draw.rect(surface, fill_color, btn_self.rect)

            if btn_self.theme.border_width > 0:
                pygame.draw.rect(
                    surface, btn_self.theme.border_color, btn_self.rect, btn_self.theme.border_width
                )

            font = btn_self._font if btn_self._font is not None else btn_self.theme.font
            lbl_col = btn_self._label_color()
            cache_key = (btn_self.text, id(font), lbl_col, btn_self.rect.centerx, btn_self.rect.centery)
            if getattr(btn_self, "_cached_txt_key", None) != cache_key:
                from gale.text import Text
                btn_self._cached_txt_key = cache_key
                btn_self._cached_txt_obj = Text(
                    btn_self.text,
                    font,
                    btn_self.rect.centerx,
                    btn_self.rect.centery,
                    lbl_col,
                    center=True,
                )
            btn_self._cached_txt_obj.render(surface)
        Button.render = cached_btn_render

        # Generous touch target for Checkbox on mobile / touch displays
        from gale.ui.checkbox import Checkbox
        from src.os_tools import is_android
        orig_chk_contains = Checkbox.contains
        def touch_friendly_chk_contains(chk_self, position):
            if is_android():
                # Inflate touch box by 24px horizontally and 18px vertically for finger taps
                return chk_self.rect.inflate(24, 18).collidepoint(position)
            return orig_chk_contains(chk_self, position)
        Checkbox.contains = touch_friendly_chk_contains
        
        try:
            import pygame._sdl2.controller as _sdl2_controller
            _sdl2_controller.init()
            InputHandler._real_gamepads = {}
            
            original_open = InputHandler._open_gamepad.__func__
            def patched_open(cls, device_index):
                original_open(cls, device_index)
                if _sdl2_controller.is_controller(device_index):
                    c = _sdl2_controller.Controller(device_index)
                    c.init()
                    cls._real_gamepads[device_index] = c
            InputHandler._open_gamepad = classmethod(patched_open)
            
            # --- FIX GALE AXIS NORMALIZATION BUG ---
            # Gale's GamepadAxisData has a flaw: `value if abs(value) <= 1.0 else value / 32768.0`
            # If SDL sends a tiny raw value like -1 or 1 (microscopic drift), Gale treats it as -1.0 or 1.0 (100% input).
            from gale.input_handler import GamepadAxisData
            original_axis_init = GamepadAxisData.__init__
            def patched_axis_init(self, event):
                original_axis_init(self, event)
                # Force correct normalization for Pygame 2 which always sends raw int16
                self.value = event.value / 32768.0
            GamepadAxisData.__init__ = patched_axis_init
            
        except Exception as e:
            pass
            
        InputHandler.init_gamepads()
        
        pygame.mixer.set_num_channels(32)
        
        from src import display
        display.init_display()

        from src import config
        from src.os_tools import is_android
        if is_android():
            # On Android, hardware VSYNC (eglSwapBuffers) dictates pacing.
            # Avoid software Clock.tick() sleep which causes beat frequency / vsync stutter
            # and triggers Xiaomi/MIUI AdaptiveSync downclocking to 5-10 Hz.
            self.fps = 0
            config.set("fps_limit", "auto", auto_save=False)
        else:
            self.set_fps_limit(config.get("fps_limit", 60), save=False)

        self.state_stack = VibeStateStack()
        self.state_stack.push(OpeningState(self.state_stack))

        from src.os_tools import is_android
        if not is_android():
            from src.discord_rpc import DiscordRPCManager
            self.discord_rpc = DiscordRPCManager()
            self.discord_rpc.start()

    def set_fps_limit(self, fps_val: Any, save: bool = True) -> None:
        from src import config
        from src.os_tools import is_android
        config.set("fps_limit", fps_val, auto_save=save)
        if is_android():
            self.fps = 0
        else:
            self.fps = config.get_effective_fps()

    def _Game__update(self, dt: float) -> None:
        """Advance fixed_update deterministically with clamp to prevent death spiral."""
        import time
        t0 = time.perf_counter()
        dt = min(dt, 0.05)
        self._accumulator += dt

        max_steps = 3
        while self._accumulator >= self.fixed_timestep and max_steps > 0:
            self.fixed_update()
            self._accumulator -= self.fixed_timestep
            max_steps -= 1

        if self._accumulator >= self.fixed_timestep:
            self._accumulator = min(self._accumulator, self.fixed_timestep)

        from gale.timer import Timer
        Timer.update(dt)
        self.update(dt)
        self._last_update_ms = (time.perf_counter() - t0) * 1000.0

    def _Game__render(self) -> None:
        """Optimized render loop with granular frame profiler."""
        import time
        t0 = time.perf_counter()
        screen_size = self.screen.get_size()
        virt_size = (self.virtual_width, self.virtual_height)

        t_render = 0.0
        t_scale = 0.0
        t_swap = 0.0

        if screen_size == virt_size:
            self.screen.fill((0, 0, 0))
            t_r0 = time.perf_counter()
            self.render(self.screen)
            t_render = time.perf_counter() - t_r0
        else:
            self.render_surface.fill((0, 0, 0))
            t_r0 = time.perf_counter()
            self.render(self.render_surface)
            t_render = time.perf_counter() - t_r0

            t_s0 = time.perf_counter()
            pygame.transform.scale(self.render_surface, screen_size, self.screen)
            t_scale = time.perf_counter() - t_s0

        t_u0 = time.perf_counter()
        pygame.display.update()
        t_swap = time.perf_counter() - t_u0

        total_frame_t = time.perf_counter() - t0

        if not hasattr(self, "_perf_frame"):
            self._perf_frame = 0
            self._perf_accum = {"total": 0.0, "update": 0.0, "render": 0.0, "scale": 0.0, "swap": 0.0}

        self._perf_frame += 1
        self._perf_accum["total"] += total_frame_t
        self._perf_accum["update"] += getattr(self, "_last_update_ms", 0.0)
        self._perf_accum["render"] += t_render * 1000.0
        self._perf_accum["scale"] += t_scale * 1000.0
        self._perf_accum["swap"] += t_swap * 1000.0

        if self._perf_frame % 10 == 0:
            avg_tot = self._perf_accum["total"] / 10.0 * 1000.0
            avg_upd = self._perf_accum["update"] / 10.0
            avg_ren = self._perf_accum["render"] / 10.0
            avg_sca = self._perf_accum["scale"] / 10.0
            avg_swap = self._perf_accum["swap"] / 10.0
            fps = self.clock.get_fps()
            top_state = self.state_stack.states[-1].__class__.__name__ if self.state_stack.states else "None"
            msg = (f"[FRAME {self._perf_frame:04d}] state={top_state} FPS={fps:4.1f} | FrameTot={avg_tot:5.1f}ms "
                   f"(Upd={avg_upd:4.1f}ms, Render={avg_ren:4.1f}ms, Scale={avg_sca:4.1f}ms, Swap/VSync={avg_swap:4.1f}ms) "
                   f"| scr={screen_size} virt={virt_size}")
            if hasattr(self, "logger") and self.logger:
                self.logger.info(msg)
            else:
                print(msg)
            self._perf_accum = {"total": 0.0, "update": 0.0, "render": 0.0, "scale": 0.0, "swap": 0.0}

    def fixed_update(self) -> None:
        state = self.state_stack.states[-1]
        fixed_update = getattr(state, "fixed_update", None)
        if fixed_update is not None:
            fixed_update()

    def update(self, dt: float) -> None:
        import settings
        settings.RENDER_ALPHA = min(1.0, max(0.0, self._accumulator / self.fixed_timestep))
        self.state_stack.update(dt)
        if self.state_stack.states and hasattr(self, "discord_rpc"):
            self.discord_rpc.update_from_state(self.state_stack.states[-1])

    def render(self, surface: pygame.Surface) -> None:
        self.state_stack.render(surface)
        import settings
        if getattr(settings, 'SHOW_FPS', False):
            from gale.text import render_text
            fps = int(self.clock.get_fps())
            render_text(
                surface,
                f"{fps} FPS",
                settings.FONTS["minecraft_small"],
                settings.VIRTUAL_WIDTH - 44,
                4,
                (255, 255, 100),
                shadowed=True,
            )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "toggle_fullscreen" and input_data.pressed:
            from src import display
            display.toggle_fullscreen()
            self.is_fullscreen = display.is_fullscreen()
            return
        elif input_id == "quit" and input_data.pressed:
            self.quit()
        else:
            self.state_stack.on_input(input_id, input_data)

    def quit(self) -> None:
        if hasattr(self, "discord_rpc"):
            self.discord_rpc.close()
        super().quit()