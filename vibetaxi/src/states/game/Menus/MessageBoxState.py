from typing import Any, Callable, Dict, Optional
import pygame

import settings
from gale.state import BaseState
from gale.timer import Timer
from gale.ui.button import Button
from gale.ui.container import Container
from gale.ui.label import Label
from src.gui.TypewriterTextBox import TypewriterTextBox
from gale.ui.manager import UIManager
from gale.ui.panel import Panel

class MessageBoxState(BaseState):
    def __init__(self, state_machine: Any, title: str, message: str, on_close: Callable = None) -> None:
        super().__init__(state_machine)
        self.fade_alpha = 0.0
        self.panel_width = 320
        self.panel_height = 124
        self.panel_y = -200
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - self.panel_height / 2
        self.is_exiting = False
        
        self.on_close_callback = on_close
        
        from src.themes import BUTTON_THEME, PANEL_THEME, LABEL_THEME, TEXTBOX_THEME
        panel_x = settings.VIRTUAL_WIDTH / 2 - self.panel_width / 2
        self.panel = Panel(
            panel_x, 
            self.panel_y, 
            self.panel_width, self.panel_height,
            theme=PANEL_THEME
        )
        
        self.label_title = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 12, 
            title, 
            theme=LABEL_THEME,
            center=True
        )
        
        self.text_box = TypewriterTextBox(
            panel_x + 15, 
            self.panel_y + 28, 
            self.panel_width - 30, 
            54, 
            message, 
            lines_per_page=4,
            on_close=self._on_ok,
            theme=TEXTBOX_THEME
        )
        
        self.btn_ok = Button(
            settings.VIRTUAL_WIDTH / 2 - 45, 
            self.panel_y + 88, 
            90, 24, 
            "OK", 
            on_click=self._on_button_click,
            theme=BUTTON_THEME
        )
        
        self.container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[
            self.panel, self.label_title, self.text_box, self.btn_ok
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
        
        for state in self.state_machine.states:
            if hasattr(state, "pause_audio"):
                state.pause_audio()
            if hasattr(state, "reset_inputs"):
                state.reset_inputs()
        
        Timer.tween(0.3, [(self, {"fade_alpha": 180.0})])
        Timer.tween(0.5, [(self, {"panel_y": self.target_y})], ease_function_name="out_cubic")
        
    def update_ui_y(self):
        self.panel.y = self.panel_y
        self.label_title.y = self.panel_y + 12
        self.text_box.y = self.panel_y + 28
        self.btn_ok.y = self.panel_y + 88
        
    def _on_button_click(self):
        if hasattr(self.text_box, "is_typing") and self.text_box.is_typing:
            self.text_box.advance()
        elif self.text_box.has_next_page:
            self.text_box.next_page()
        else:
            self._on_ok()

    def _on_ok(self):
        if self.is_exiting: return
        self.is_exiting = True
        if "press" in settings.SOUNDS: settings.SOUNDS["press"].play()
        
        def on_finish():
            self.state_machine.pop()
            for state in self.state_machine.states:
                if hasattr(state, "resume_audio"):
                    state.resume_audio()
                if hasattr(state, "reset_inputs"):
                    state.reset_inputs()
            if self.on_close_callback is not None:
                self.on_close_callback()
            
        Timer.tween(0.3, [(self, {"fade_alpha": 0.0})])
        Timer.tween(0.5, [(self, {"panel_y": -200})], ease_function_name="in_cubic", on_finish=on_finish)

    def update(self, dt: float):
        self.update_ui_y()
        if self.text_box.has_next_page:
            self.btn_ok.text = "Next"
        else:
            self.btn_ok.text = "OK"
        self.ui.update(dt)

    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
            
        self.ui.render(surface)
