"""
A reusable horizontal Slider widget for numerical inputs in Gale UI.
Supports gamepad/keyboard directional navigation (left/right to adjust)
and mouse clicking/dragging.
"""

from typing import Callable, Optional, Tuple
import pygame

from gale.input_handler import MouseClickData
from gale.ui.widget import Direction, Widget
from gale.ui.theme import Theme


class Slider(Widget):
    """
    A horizontal slider allowing value adjustment between min_val and max_val.
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        value: float = 0.5,
        min_val: float = 0.0,
        max_val: float = 1.0,
        step: float = 0.05,
        format_str: Optional[str] = "{:.0%}",
        on_change: Optional[Callable[[float], None]] = None,
        theme: Optional[Theme] = None,
    ) -> None:
        super().__init__(x, y, width, height, theme=theme)
        self.min_val: float = min_val
        self.max_val: float = max_val
        self.step: float = step
        self.value: float = max(min_val, min(max_val, value))
        self.format_str: Optional[str] = format_str
        self.on_change: Optional[Callable[[float], None]] = on_change
        self.focusable: bool = True
        self.is_dragging: bool = False

    @property
    def ratio(self) -> float:
        range_val = self.max_val - self.min_val
        if range_val <= 0:
            return 0.0
        return max(0.0, min(1.0, (self.value - self.min_val) / range_val))

    def set_value(self, new_val: float, notify: bool = True) -> None:
        clamped = max(self.min_val, min(self.max_val, new_val))
        if round(clamped, 4) != round(self.value, 4):
            self.value = clamped
            if notify and self.on_change is not None:
                self.on_change(self.value)

    def _update_from_pos(self, mouse_x: float) -> None:
        track_w = self.width - 12
        if track_w <= 0:
            return
        rel_x = max(0.0, min(track_w, mouse_x - (self.x + 6)))
        ratio = rel_x / track_w
        raw_val = self.min_val + ratio * (self.max_val - self.min_val)
        # Snap to step if reasonable
        if self.step > 0:
            raw_val = round(raw_val / self.step) * self.step
        self.set_value(raw_val)

    def on_navigate(self, direction: Direction) -> bool:
        if not self.enabled:
            return False

        dx, dy = direction
        if dx != 0:
            self.set_value(self.value + dx * self.step)
            return True

        # Allow vertical navigation to move focus to other widgets
        return False

    def on_mouse_click(
        self, position: Tuple[float, float], data: MouseClickData
    ) -> bool:
        if not self.enabled:
            return False

        if self.contains(position):
            if data.pressed:
                self.is_dragging = True
                self._update_from_pos(position[0])
            elif data.released:
                self.is_dragging = False
            return True

        if data.released and self.is_dragging:
            self.is_dragging = False

        return False

    def on_mouse_motion(self, position: Tuple[float, float]) -> None:
        if self.is_dragging:
            if pygame.mouse.get_pressed()[0]:
                self._update_from_pos(position[0])
            else:
                self.is_dragging = False

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        track_h = max(4, int(self.height * 0.35))
        track_y = int(self.y + (self.height - track_h) / 2)
        track_x = int(self.x + 6)
        track_w = int(self.width - 12)

        # Background track
        track_rect = pygame.Rect(track_x, track_y, track_w, track_h)
        bg_col = self.theme.background_color
        pygame.draw.rect(surface, bg_col, track_rect, border_radius=3)

        # Active fill track
        fill_w = int(track_w * self.ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(track_x, track_y, fill_w, track_h)
            fill_col = self.theme.accent_color
            pygame.draw.rect(surface, fill_col, fill_rect, border_radius=3)

        # Track border
        border_col = self.theme.focus_color if self.focused else self.theme.border_color
        pygame.draw.rect(surface, border_col, track_rect, width=1, border_radius=3)

        # Handle knob
        knob_radius = int(self.height * 0.42)
        knob_cx = int(track_x + fill_w)
        knob_cy = int(self.y + self.height / 2)

        # Knob fill
        knob_col = self.theme.focus_color if self.focused else self.theme.border_color
        pygame.draw.circle(surface, bg_col, (knob_cx, knob_cy), knob_radius)
        pygame.draw.circle(surface, knob_col, (knob_cx, knob_cy), knob_radius - 1)
        pygame.draw.circle(surface, (255, 255, 255), (knob_cx, knob_cy), knob_radius, width=1)

        # Optional value text inside or alongside
        if self.format_str and self.theme.font:
            try:
                val_text = self.format_str.format(self.value)
                text_surf = self.theme.font.render(val_text, True, self.theme.text_color)
                # Render text centered above or at the right
                text_y = int(self.y + (self.height - text_surf.get_height()) / 2)
                surface.blit(text_surf, (self.x + self.width + 6, text_y))
            except Exception:
                pass
