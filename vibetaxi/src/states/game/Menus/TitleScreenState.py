import pygame
import settings

from typing import Dict, Any
from gale.state import BaseState
from gale.text import render_text

from src.states.game.Gameplay.PlayState import PlayState

class TitleScreenState(BaseState):
    def enter(self, enter_params: Dict[str, Any] = None):
        pass

    def exit(self):
        pass

    def update(self, dt: float):
        pass

    def on_input(self, input_id, input_data):
        if input_id == "mouse_click" and input_data.pressed:
            self.state_machine.pop()
            self.state_machine.push(PlayState(self.state_machine))


    def render(self, surface: pygame.Surface):
        render_text(
            surface,
            "Vibe Taxi",
            settings.FONTS["big"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            (255, 255, 255),
            center=True
        )
