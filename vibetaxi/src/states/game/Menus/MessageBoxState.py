from typing import Any, Callable, Dict, Optional
import pygame

import settings
from gale.state import BaseState
from gale.timer import Timer
from gale.ui.button import Button
from gale.ui.container import Container
from gale.ui.label import Label
from gale.ui.manager import UIManager
from gale.ui.panel import Panel

class MessageBoxState(BaseState):
    def __init__(self, state_machine: Any, title: str, message: str, on_close: Callable) -> None:
        super().__init__(state_machine)
        self.fade_alpha = 0.0
        self.panel_y = -200
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - 50
        self.is_exiting = False
        
        self.on_close_callback = on_close
        
        from src.themes import BUTTON_THEME, PANEL_THEME, LABEL_THEME
        self.panel = Panel(
            settings.VIRTUAL_WIDTH / 2 - 150, 
            self.panel_y, 
            300, 100,
            theme=PANEL_THEME
        )
        
        self.label_title = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 20, 
            title, 
            theme=LABEL_THEME,
            center=True
        )
        
        self.label_msg = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 45, 
            message, 
            theme=LABEL_THEME,
            center=True
        )
        
        self.btn_ok = Button(
            settings.VIRTUAL_WIDTH / 2 - 50, 
            self.panel_y + 70, 
            100, 25, 
            "OK", 
            on_click=self._on_ok,
            theme=BUTTON_THEME
        )
        
        self.container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[
            self.panel, self.label_title, self.label_msg, self.btn_ok
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
        self.panel_y = -200
        self.is_exiting = False
        self.update_ui_y()
        
        Timer.tween(0.3, [(self, {"fade_alpha": 180.0})])
        Timer.tween(0.5, [(self, {"panel_y": self.target_y})], ease_function_name="out_cubic")
        
    def update_ui_y(self):
        self.panel.y = self.panel_y
        self.label_title.y = self.panel_y + 20
        self.label_msg.y = self.panel_y + 45
        self.btn_ok.y = self.panel_y + 70
        
    def _on_ok(self):
        if self.is_exiting: return
        self.is_exiting = True
        if "press" in settings.SOUNDS: settings.SOUNDS["press"].play()
        
        def on_finish():
            self.state_machine.pop()
            if self.on_close_callback:
                self.on_close_callback()
            
        Timer.tween(0.3, [(self, {"fade_alpha": 0.0})])
        Timer.tween(0.5, [(self, {"panel_y": -200})], ease_function_name="in_cubic", on_finish=on_finish)

    def update(self, dt: float):
        self.update_ui_y()
        self.ui.update(dt)

    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
            
        self.ui.render(surface)
