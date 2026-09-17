import pygame
import settings
from typing import Dict, Any, Optional

from gale.state import BaseState
from gale.timer import Timer
from gale.ui.manager import UIManager
from gale.ui.container import Container
from gale.ui.panel import Panel
from gale.ui.button import Button
from gale.ui.label import Label
from gale.ui.theme import Theme
from gale.ui.text_input import TextInput

class NewRecordState(BaseState):
    def __init__(self, state_machine: Any, mode: str, score: float, records: dict, next_state_callback: callable) -> None:
        super().__init__(state_machine)
        self.mode = mode
        self.score = score
        self.records = records
        self.next_state_callback = next_state_callback
        
        self.fade_alpha = 0.0
        self.panel_y = -300
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - 80
        self.is_exiting = False
        
        panel_width = 240
        panel_height = 160
        from src.themes import BUTTON_THEME, LABEL_GOLD_THEME, LABEL_THEME, INPUT_THEME, PANEL_THEME
        self.panel = Panel(
            settings.VIRTUAL_WIDTH / 2 - panel_width / 2, 
            self.panel_y, 
            panel_width, panel_height,
            theme=PANEL_THEME
        )
        
        self.label_title = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 20, 
            "New Record!", 
            theme=LABEL_GOLD_THEME,
            center=True
        )
        
        self.label_score = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 50, 
            f"Score: {self.score}", 
            theme=LABEL_THEME,
            center=True
        )
        
        self.text_input = TextInput(
            settings.VIRTUAL_WIDTH / 2 - 80, self.panel_y + 80,
            160, 25,
            max_length=10,
            theme=INPUT_THEME
        )
        
        self.btn_submit = Button(
            settings.VIRTUAL_WIDTH / 2 - 40, self.panel_y + 115,
            80, 25,
            "Save",
            on_click=self.on_submit_click,
            theme=BUTTON_THEME
        )
        
        self.container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[
            self.panel, self.label_title, self.label_score, self.text_input, self.btn_submit
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
        self.panel_y = -300
        self.is_exiting = False
        self.update_ui_y()
        self.text_input.focused = True
        
        def focus_input():
            self.text_input.focused = True
            
        Timer.tween(0.3, [(self, {"fade_alpha": 180.0})])
        Timer.tween(0.5, [(self, {"panel_y": self.target_y})], ease_function_name="out_cubic", on_finish=focus_input)
        
    def update_ui_y(self):
        self.panel.y = self.panel_y
        self.label_title.y = self.panel_y + 20
        self.label_score.y = self.panel_y + 50
        self.text_input.y = self.panel_y + 80
        self.btn_submit.y = self.panel_y + 115
        
    def on_submit_click(self):
        if self.is_exiting: return
        settings.SOUNDS["press"].play()
        self.is_exiting = True
        
        name = self.text_input.text.strip()
        if not name:
            name = "Unknown"
            
        # Save record
        self.records[self.mode].append({"name": name, "score": self.score})
        self.records[self.mode].sort(key=lambda x: x["score"], reverse=True)
        if len(self.records[self.mode]) > 10:
            self.records[self.mode] = self.records[self.mode][:10]
            
        settings.SAVE_MANAGER.save("records", self.records)
        
        def continue_game():
            self.state_machine.pop()
            self.next_state_callback()
            
        Timer.tween(0.3, [(self, {"fade_alpha": 0.0})])
        Timer.tween(0.5, [(self, {"panel_y": -300})], ease_function_name="in_cubic", on_finish=continue_game)

    def update(self, dt: float):
        self.update_ui_y()
        self.ui.update(dt)

    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        if getattr(self, "fade_alpha", 0.0) > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
            
        self.ui.render(surface)
