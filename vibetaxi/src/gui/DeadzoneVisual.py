"""
Visual indicator showing gamepad deadzone as two concentric circles,
with real-time analog stick deflection feedback.
"""

import math
from typing import Optional
import pygame

from gale.ui.widget import Widget
from gale.ui.theme import Theme


class DeadzoneVisual(Widget):
    """
    Renders two concentric circles:
    - Outer circle: 100% full analog stick range.
    - Inner circle: active deadzone threshold percentage.
    - Active stick cursor: live dot showing current analog stick deflection.
    """

    def __init__(
        self,
        x: float,
        y: float,
        size: float = 44,
        deadzone: float = 0.25,
        theme: Optional[Theme] = None,
    ) -> None:
        super().__init__(x, y, size, size, theme=theme)
        self.deadzone: float = max(0.01, min(0.99, deadzone))
        self.focusable: bool = False

    def set_deadzone(self, deadzone: float) -> None:
        self.deadzone = max(0.01, min(0.99, deadzone))

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        cx = int(self.x + self.width / 2)
        cy = int(self.y + self.height / 2)
        r_outer = int(min(self.width, self.height) / 2 - 3)
        r_inner = max(2, int(r_outer * self.deadzone))

        # Base background plate
        plate_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(plate_surf, (25, 20, 30, 200), (self.width // 2, self.height // 2), r_outer)

        # Inner deadzone shaded area (reddish/warning tint)
        pygame.draw.circle(plate_surf, (220, 60, 70, 90), (self.width // 2, self.height // 2), r_inner)
        surface.blit(plate_surf, (self.x, self.y))

        # Crosshairs
        pygame.draw.line(surface, (90, 80, 100), (cx - r_outer + 2, cy), (cx + r_outer - 2, cy), 1)
        pygame.draw.line(surface, (90, 80, 100), (cx, cy - r_outer + 2), (cx, cy + r_outer - 2), 1)

        # Inner deadzone boundary
        pygame.draw.circle(surface, (255, 100, 110), (cx, cy), r_inner, width=1)

        # Outer range boundary
        border_col = self.theme.border_color if self.theme else (220, 220, 230)
        pygame.draw.circle(surface, border_col, (cx, cy), r_outer, width=1)

        # Check live gamepad stick deflection
        stick_x, stick_y = 0.0, 0.0
        try:
            if pygame.joystick.get_count() > 0:
                js = pygame.joystick.Joystick(0)
                if not js.get_init():
                    js.init()
                stick_x = js.get_axis(0)
                stick_y = js.get_axis(1)
        except Exception:
            pass

        mag = math.hypot(stick_x, stick_y)
        dot_x = int(cx + max(-1.0, min(1.0, stick_x)) * r_outer)
        dot_y = int(cy + max(-1.0, min(1.0, stick_y)) * r_outer)

        if mag > 0.05:
            # Active indicator
            dot_col = (100, 255, 120) if mag >= self.deadzone else (255, 180, 50)
            pygame.draw.circle(surface, dot_col, (dot_x, dot_y), 4)
            pygame.draw.circle(surface, (255, 255, 255), (dot_x, dot_y), 4, width=1)
        else:
            # Center idle dot
            pygame.draw.circle(surface, (160, 160, 180), (cx, cy), 2)
