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

class PauseState(BaseState):
    def __init__(self, state_machine: Any) -> None:
        super().__init__(state_machine)
        self.fade_alpha = 0.0
        self.panel_y = -200
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - 60
        self.is_exiting = False
        
        panel_width = 200
        panel_height = 120
        self.panel = Panel(
            settings.VIRTUAL_WIDTH / 2 - panel_width / 2, 
            self.panel_y, 
            panel_width, panel_height
        )
        
        lbl_theme = Theme(font=settings.FONTS["minecraft"], text_color=pygame.Color(255, 255, 255))
        self.label_title = Label(
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 20, 
            "Paused", 
            theme=lbl_theme,
            center=True
        )
        
        btn_theme = Theme(
            font=settings.FONTS["minecraft"],
            background_color=pygame.Color(100, 60, 90),
            hover_color=pygame.Color(150, 90, 120),
            text_color=pygame.Color(255, 255, 255),
            border_color=pygame.Color(255, 255, 255),
            border_width=1
        )
        
        self.btn_resume = Button(
            settings.VIRTUAL_WIDTH / 2 - 60, self.panel_y + 50,
            120, 25,
            "Continue",
            on_click=self.on_resume_click,
            theme=btn_theme
        )
        
        self.btn_exit = Button(
            settings.VIRTUAL_WIDTH / 2 - 60, self.panel_y + 85,
            120, 25,
            "Exit",
            on_click=self.on_exit_click,
            theme=btn_theme
        )
        
        self.container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[
            self.panel, self.label_title, self.btn_resume, self.btn_exit
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
        
        pygame.mixer.music.pause()
        # Pause game sounds?
        
        Timer.tween(0.3, [(self, {"fade_alpha": 128.0})])
        Timer.tween(0.5, [(self, {"panel_y": self.target_y})], ease_function_name="out_cubic")
        
    def update_ui_y(self):
        self.panel.y = self.panel_y
        self.label_title.y = self.panel_y + 20
        self.btn_resume.y = self.panel_y + 50
        self.btn_exit.y = self.panel_y + 85
        
    def on_resume_click(self):
        if self.is_exiting: return
        if "unpause" in settings.SOUNDS: settings.SOUNDS["unpause"].play()
        self.is_exiting = True
        
        def resume_game():
            pygame.mixer.music.unpause()
            self.state_machine.pop()
            
        Timer.tween(0.3, [(self, {"fade_alpha": 0.0})])
        Timer.tween(0.5, [(self, {"panel_y": -200})], ease_function_name="in_cubic", on_finish=resume_game)
        
    def on_exit_click(self):
        if self.is_exiting: return
        settings.SOUNDS["press"].play()
        self.is_exiting = True
        
        def exit_to_title():
            from src.states.game.Menus.TitleScreenState import TitleScreenState
            while len(self.state_machine.states) > 0:
                self.state_machine.pop()
            self.state_machine.push(TitleScreenState(self.state_machine))
            
        Timer.tween(0.5, [(self, {"fade_alpha": 255.0})], on_finish=exit_to_title)

    def update(self, dt: float):
        self.update_ui_y()
        self.ui.update(dt)

    def on_input(self, input_id, input_data):
        if input_id == "pause" and input_data.pressed:
            self.on_resume_click()
            return
        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        if getattr(self, "fade_alpha", 0.0) > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
            
        self.ui.render(surface)
