import pygame
import settings

from typing import Dict, Any, Optional
from gale.state import BaseState
from gale.timer import Timer
from gale.ui.manager import UIManager
from gale.ui.panel import Panel
from gale.ui.label import Label
from gale.ui.container import Container

from src.states.game.Menus.TitleScreenState import TitleScreenState

class GameOverState(BaseState):
    def __init__(self, state_machine: Any) -> None:
        super().__init__(state_machine)
        self.fade_alpha = 0.0
        self.panel_y = -200
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - 50
        self.is_exiting = False
        
        self.panel = Panel(
            settings.VIRTUAL_WIDTH / 2 - 100, 
            self.panel_y, 
            200, 100
        )
        self.label_title = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 30, 
            "¡Perdiste!", 
            center=True
        )
        self.label_prompt = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 70, 
            "Haz clic para salir", 
            center=True
        )
        
        self.container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[
            self.panel, self.label_title, self.label_prompt
        ])
        
        self.ui = UIManager(
            self.container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )
        
    def enter(self, enter_params: Optional[Dict[str, Any]] = None):
        self.fade_alpha = 0.0
        self.exit_alpha = 0.0
        self.panel_y = -200
        self.is_exiting = False
        self.update_ui_y()
        
        Timer.tween(1.0, [(self, {"fade_alpha": 180.0})])
        Timer.tween(1.0, [(self, {"panel_y": self.target_y})], ease_function_name="out_cubic")
        
    def update_ui_y(self):
        self.panel.y = self.panel_y
        self.label_title.y = self.panel_y + 30
        self.label_prompt.y = self.panel_y + 70
        
    def on_exit_click(self):
        if self.is_exiting:
            return
        self.is_exiting = True
        Timer.tween(1.0, [(self, {"exit_alpha": 255.0})], on_finish=self.return_to_title)
        
    def return_to_title(self):
        # Pop all states properly to ensure exit() is called
        while len(self.state_machine.states) > 0:
            self.state_machine.pop()
        self.state_machine.push(TitleScreenState(self.state_machine))

    def update(self, dt: float):
        self.update_ui_y()
        self.ui.update(dt)

    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)
        
        if input_id == "mouse_click" and input_data.pressed:
            if self.panel_y >= self.target_y:
                self.on_exit_click()

    def render(self, surface: pygame.Surface):
        if getattr(self, "fade_alpha", 0.0) > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
            
        self.ui.render(surface)
        
        if getattr(self, "exit_alpha", 0.0) > 0:
            exit_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            exit_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.exit_alpha)))))
            surface.blit(exit_surf, (0, 0))
