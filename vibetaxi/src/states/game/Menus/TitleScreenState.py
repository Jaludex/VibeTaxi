import pygame
import settings

from typing import Dict, Any
from gale.state import BaseState
from gale.text import render_text

class TitleScreenState(BaseState):
    def enter(self, enter_params: Dict[str, Any] = None):
        pass

    def exit(self):
        pass

    def update(self, dt: float):
        pass

    def on_input(self, input_id, input_data):
        pass

    def render(self, surface: pygame.Surface):
        render_text(
            surface,
            "Test",
            settings.FONTS["big"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            (255, 255, 255),
            center=True
        )
