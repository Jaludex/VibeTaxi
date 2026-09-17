import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateStack

from src.states.game.Menus.OpeningState import OpeningState


class VibeTaxi(Game):
    def init(self) -> None:
        from gale.ui.theme import Theme, set_default_theme
        import settings
        set_default_theme(Theme(
            font=settings.FONTS["minecraft"],
            background_color=pygame.Color(69, 40, 60),
            border_color=pygame.Color(255, 255, 255)
        ))
        
        self.state_stack = StateStack()
        self.state_stack.push(OpeningState(self.state_stack))

    def fixed_update(self) -> None:
        state = self.state_stack.states[-1]
        fixed_update = getattr(state, "fixed_update", None)
        if fixed_update is not None:
            fixed_update()

    def update(self, dt: float) -> None:
        self.state_stack.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_stack.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            self.quit()
        else:
            self.state_stack.on_input(input_id, input_data)