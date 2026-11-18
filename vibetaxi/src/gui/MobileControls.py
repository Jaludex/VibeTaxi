"""
Mobile on-screen controls for VibeTaxi.
Provides touch buttons for Brake, Drift, Radio tuning, Pause, and an optional Virtual Joystick.
Supports both SDL2 multi-touch (pygame.FINGER*) and mouse simulation fallback.
"""

import math
from typing import Dict, Optional, Tuple
import pygame

import settings
from src import commands
from gale.input_handler import InputHandler, KeyboardData
from gale.ui.theme import Theme
from gale.ui.widget import Widget
from src.mouse_tools import physical_to_virtual


class TouchButton(Widget):
    """An on-screen touch button that detects hold and release states."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        label: str,
        base_color: Tuple[int, int, int, int],
        active_color: Tuple[int, int, int, int],
        on_press=None,
        on_release=None,
        font: Optional[pygame.font.Font] = None,
        border_radius: int = 8,
    ):
        super().__init__(x, y, width, height)
        self.label = label
        self.base_color = base_color
        self.active_color = active_color
        self.on_press = on_press
        self.on_release = on_release
        self.font = font or settings.FONTS.get("minecraft_small")
        self.border_radius = border_radius
        self.is_pressed = False
        self.assigned_finger_id: Optional[int] = None
        self._normal_surf = self._create_surface(False)
        self._pressed_surf = self._create_surface(True)

    def _create_surface(self, pressed: bool) -> pygame.Surface:
        surf = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
        color = self.active_color if pressed else self.base_color
        rect = pygame.Rect(0, 0, int(self.width), int(self.height))

        pygame.draw.rect(surf, color, rect, border_radius=self.border_radius)
        border_col = (255, 255, 255, 200) if pressed else (200, 200, 200, 140)
        pygame.draw.rect(surf, border_col, rect, width=2, border_radius=self.border_radius)

        if self.label and self.font:
            text_col = (255, 255, 255) if not pressed else (255, 255, 100)
            txt = self.font.render(self.label, True, text_col)
            txt_x = (self.width - txt.get_width()) // 2
            txt_y = (self.height - txt.get_height()) // 2
            surf.blit(txt, (txt_x, txt_y))
        return surf

    def contains(self, position: Tuple[float, float]) -> bool:
        # Generous hit area (12px expansion for comfortable finger taps)
        return self.rect.inflate(12, 12).collidepoint(position)

    def press(self, finger_id: Optional[int] = None):
        if not self.is_pressed:
            self.is_pressed = True
            self.assigned_finger_id = finger_id
            if self.on_press:
                self.on_press()

    def release(self):
        if self.is_pressed:
            self.is_pressed = False
            self.assigned_finger_id = None
            if self.on_release:
                self.on_release()

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        surf = self._pressed_surf if self.is_pressed else self._normal_surf
        surface.blit(surf, (int(self.x), int(self.y)))


class VirtualJoystick:
    """A floating/dynamic on-screen analog thumbstick for steering and accelerating.
    
    Centers dynamically wherever the player touches on the left side of the screen.
    """

    def __init__(
        self,
        default_x: float = 70.0,
        default_y: float = 285.0,
        base_radius: float = 42.0,
        stick_radius: float = 20.0,
        center_x: Optional[float] = None,
        center_y: Optional[float] = None,
    ):
        self.default_x = center_x if center_x is not None else default_x
        self.default_y = center_y if center_y is not None else default_y
        self.center_x = self.default_x
        self.center_y = self.default_y
        self.base_radius = base_radius
        self.stick_radius = stick_radius
        self.stick_x = self.default_x
        self.stick_y = self.default_y
        self.active_finger_id: Optional[int] = None
        self.is_active: bool = False
        self.dx = 0.0  # Normalized -1.0 to 1.0
        self.dy = 0.0

        # Pre-render base and stick heads to avoid allocations every frame
        self._base_surf = pygame.Surface((int(self.base_radius * 2 + 4), int(self.base_radius * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            self._base_surf,
            (40, 40, 50, 130),
            (int(self.base_radius + 2), int(self.base_radius + 2)),
            int(self.base_radius),
        )
        pygame.draw.circle(
            self._base_surf,
            (255, 255, 255, 190),
            (int(self.base_radius + 2), int(self.base_radius + 2)),
            int(self.base_radius),
            width=2,
        )

        # Faint idle guide ring
        self._idle_guide_surf = pygame.Surface((int(self.base_radius * 2 + 4), int(self.base_radius * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            self._idle_guide_surf,
            (255, 255, 255, 50),
            (int(self.base_radius + 2), int(self.base_radius + 2)),
            int(self.base_radius),
            width=2,
        )

        self._stick_idle_surf = self._create_stick_surf((220, 220, 220, 90))
        self._stick_active_surf = self._create_stick_surf((255, 210, 60, 220))

    def _create_stick_surf(self, color: Tuple[int, int, int, int]) -> pygame.Surface:
        surf = pygame.Surface((int(self.stick_radius * 2 + 4), int(self.stick_radius * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            color,
            (int(self.stick_radius + 2), int(self.stick_radius + 2)),
            int(self.stick_radius),
        )
        pygame.draw.circle(
            surf,
            (255, 255, 255, 220),
            (int(self.stick_radius + 2), int(self.stick_radius + 2)),
            int(self.stick_radius),
            width=2,
        )
        return surf

    def is_in_joystick_zone(self, vx: float, vy: float) -> bool:
        """Left 55% of the virtual screen is the touch drive/joystick zone."""
        return vx <= settings.VIRTUAL_WIDTH * 0.55

    def on_touch_down(self, vx: float, vy: float, finger_id: Optional[int] = None) -> bool:
        if self.active_finger_id is None and self.is_in_joystick_zone(vx, vy):
            self.active_finger_id = finger_id
            self.is_active = True
            # Center dynamically where touch lands
            self.center_x = vx
            self.center_y = vy
            self.stick_x = vx
            self.stick_y = vy
            self.dx = 0.0
            self.dy = 0.0
            return True
        return False

    def on_touch_move(self, vx: float, vy: float, finger_id: Optional[int] = None) -> bool:
        if self.active_finger_id == finger_id or (self.active_finger_id is None and finger_id is None and self.is_active):
            self.update_position(vx, vy)
            return True
        return False

    def on_touch_up(self, finger_id: Optional[int] = None) -> bool:
        if self.active_finger_id == finger_id or (finger_id is None and self.is_active):
            self.reset()
            return True
        return False

    def update_position(self, vx: float, vy: float):
        offset_x = vx - self.center_x
        offset_y = vy - self.center_y
        dist = math.hypot(offset_x, offset_y)
        max_dist = self.base_radius

        if dist > max_dist:
            scale = max_dist / dist
            offset_x *= scale
            offset_y *= scale

        self.stick_x = self.center_x + offset_x
        self.stick_y = self.center_y + offset_y
        self.dx = offset_x / max_dist if max_dist > 0 else 0.0
        self.dy = offset_y / max_dist if max_dist > 0 else 0.0

    def reset(self):
        self.center_x = self.default_x
        self.center_y = self.default_y
        self.stick_x = self.default_x
        self.stick_y = self.default_y
        self.dx = 0.0
        self.dy = 0.0
        self.active_finger_id = None
        self.is_active = False

    def render(self, surface: pygame.Surface) -> None:
        if self.is_active:
            surface.blit(
                self._base_surf,
                (int(self.center_x - self.base_radius - 2), int(self.center_y - self.base_radius - 2)),
            )
            surface.blit(
                self._stick_active_surf,
                (int(self.stick_x - self.stick_radius - 2), int(self.stick_y - self.stick_radius - 2)),
            )
        else:
            surface.blit(
                self._idle_guide_surf,
                (int(self.default_x - self.base_radius - 2), int(self.default_y - self.base_radius - 2)),
            )
            surface.blit(
                self._stick_idle_surf,
                (int(self.default_x - self.stick_radius - 2), int(self.default_y - self.stick_radius - 2)),
            )


class MobileControlsHUD:
    """
    HUD holding all mobile controls during gameplay:
    - Pause Button (top right)
    - Radio prev/next buttons (above drift and brake, right side)
    - Brake Button (bottom right)
    - Drift Button (bottom right, next to brake)
    - Joystick (if enabled in settings) or Direct Touch Handler (entire left zone)
    """

    def __init__(self, taxi, radio, state_machine):
        self.taxi = taxi
        self.radio = radio
        self.state_machine = state_machine

        vw = settings.VIRTUAL_WIDTH
        vh = settings.VIRTUAL_HEIGHT

        # Pause Button (Top-Right)
        self.btn_pause = TouchButton(
            x=vw - 36,
            y=6,
            width=30,
            height=26,
            label="II",
            base_color=(30, 30, 40, 160),
            active_color=(180, 50, 50, 220),
            on_press=self._on_pause_pressed,
            font=settings.FONTS.get("minecraft"),
        )

        # Brake / Reverse Button (Bottom-Right corner)
        self.btn_brake = TouchButton(
            x=vw - 68,
            y=vh - 66,
            width=60,
            height=58,
            label="BRAKE",
            base_color=(200, 40, 40, 150),
            active_color=(255, 60, 60, 230),
            on_press=self._on_brake_press,
            on_release=self._on_brake_release,
        )

        # Drift Button (next to Brake)
        self.btn_drift = TouchButton(
            x=vw - 134,
            y=vh - 54,
            width=58,
            height=46,
            label="DRIFT",
            base_color=(40, 140, 220, 150),
            active_color=(60, 200, 255, 230),
            on_press=self._on_drift_press,
            on_release=self._on_drift_release,
        )

        # Radio tuning buttons (Right side, above Drift and Brake)
        self.btn_prev_song = TouchButton(
            x=vw - 126,
            y=vh - 102,
            width=46,
            height=36,
            label="<",
            base_color=(40, 40, 50, 150),
            active_color=(120, 90, 180, 220),
            on_press=self._on_prev_song,
        )

        self.btn_next_song = TouchButton(
            x=vw - 68,
            y=vh - 102,
            width=46,
            height=36,
            label=">",
            base_color=(40, 40, 50, 150),
            active_color=(120, 90, 180, 220),
            on_press=self._on_next_song,
        )

        # Virtual Joystick
        self.joystick = VirtualJoystick(center_x=70, center_y=vh - 75, base_radius=42, stick_radius=20)

        self.buttons = [
            self.btn_pause,
            self.btn_brake,
            self.btn_drift,
            self.btn_prev_song,
            self.btn_next_song,
        ]

        # Multi-touch tracking
        self.touch_drive_finger_id: Optional[int] = None

    def is_joystick_mode(self) -> bool:
        return getattr(settings, "TOUCH_CONTROL_MODE", "touch") == "joystick"

    def _on_pause_pressed(self):
        from src.states.game.Gameplay.PauseState import PauseState
        from src import audio
        audio.play_sfx("pause")
        self.state_machine.push(PauseState(self.state_machine))

    def _on_brake_press(self):
        commands.BRAKE(self.taxi)

    def _on_brake_release(self):
        commands.STOP_BRAKE(self.taxi)

    def _on_drift_press(self):
        commands.DRIFT(self.taxi)

    def _on_drift_release(self):
        commands.STOP_DRIFT(self.taxi)

    def _on_prev_song(self):
        if self.radio:
            self.radio.prev_station()

    def _on_next_song(self):
        if self.radio:
            self.radio.next_station()

    def handle_touch_down(self, vx: float, vy: float, finger_id: Optional[int] = None) -> bool:
        """Handle finger touch down event. Return True if consumed."""
        # 1. Check UI buttons
        for btn in self.buttons:
            if btn.contains((vx, vy)):
                btn.press(finger_id)
                return True

        # 2. Check Virtual Joystick if in joystick mode
        if self.is_joystick_mode():
            if self.joystick.on_touch_down(vx, vy, finger_id):
                self.taxi.touch_joystick_x = self.joystick.dx
                self.taxi.touch_joystick_y = self.joystick.dy
                return True
        else:
            # Direct touch steering
            if self.touch_drive_finger_id is None:
                self.touch_drive_finger_id = finger_id
                self.taxi.touch_x = vx
                self.taxi.touch_y = vy
                self.taxi.touch_active = True
                return True

        return False

    def handle_touch_move(self, vx: float, vy: float, finger_id: Optional[int] = None) -> bool:
        """Handle finger motion."""
        # 1. Check joystick
        if self.is_joystick_mode():
            if self.joystick.on_touch_move(vx, vy, finger_id):
                self.taxi.touch_joystick_x = self.joystick.dx
                self.taxi.touch_joystick_y = self.joystick.dy
                return True
        else:
            if self.touch_drive_finger_id is not None and self.touch_drive_finger_id == finger_id:
                self.taxi.touch_x = vx
                self.taxi.touch_y = vy
                self.taxi.touch_active = True
                return True

        return False

    def handle_touch_up(self, vx: float, vy: float, finger_id: Optional[int] = None) -> bool:
        """Handle finger release."""
        # 1. Check buttons
        for btn in self.buttons:
            if btn.assigned_finger_id == finger_id or (finger_id is None and btn.is_pressed):
                btn.release()

        # 2. Check joystick
        if self.is_joystick_mode():
            if self.joystick.on_touch_up(finger_id):
                self.taxi.touch_joystick_x = 0.0
                self.taxi.touch_joystick_y = 0.0
                return True
        else:
            if self.touch_drive_finger_id is not None and self.touch_drive_finger_id == finger_id:
                self.touch_drive_finger_id = None
                self.taxi.touch_active = False
                return True

        return False

    def update(self, dt: float) -> None:
        if self.is_joystick_mode():
            self.taxi.touch_joystick_x = self.joystick.dx
            self.taxi.touch_joystick_y = self.joystick.dy

    def render(self, surface: pygame.Surface) -> None:
        # Render joystick if enabled
        if self.is_joystick_mode():
            self.joystick.render(surface)

        # Render touch buttons
        for btn in self.buttons:
            btn.render(surface)
