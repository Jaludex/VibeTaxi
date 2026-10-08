import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateStack

from src.states.game.Menus.OpeningState import OpeningState


class VibeTaxi(Game):
    def __init__(self, *args, **kwargs):
        import settings
        icon = settings.TEXTURES.get("game_icon")
        if icon:
            pygame.display.set_icon(icon)

        kwargs.setdefault("flags", pygame.SCALED | pygame.RESIZABLE)
        super().__init__(*args, **kwargs)
        self.is_fullscreen: bool = False

    def init(self) -> None:
        from gale.ui.theme import set_default_theme
        from gale.input_handler import InputHandler
        from src.themes import DEFAULT_THEME
        set_default_theme(DEFAULT_THEME)
        
        try:
            import pygame._sdl2.controller
            pygame._sdl2.controller.init()
            InputHandler._real_gamepads = {}
            
            original_open = InputHandler._open_gamepad.__func__
            def patched_open(cls, device_index):
                original_open(cls, device_index)
                if pygame._sdl2.controller.is_controller(device_index):
                    c = pygame._sdl2.controller.Controller(device_index)
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
        if input_id == "toggle_fullscreen" and input_data.pressed:
            pygame.display.toggle_fullscreen()
            self.is_fullscreen = not self.is_fullscreen
            return
        elif input_id == "quit" and input_data.pressed:
            self.quit()
        else:
            self.state_stack.on_input(input_id, input_data)