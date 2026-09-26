from src.i18n import tr
import pygame
import settings
from typing import Dict, Any, Optional

from gale.state import BaseState
from gale.timer import Timer
from gale.text import render_text
from gale.ui.manager import UIManager
from gale.ui.container import Container
from gale.ui.button import Button
from gale.ui.theme import Theme

from src.states.game.Menus.TitleScreenState import TitleScreenState

class RecordsState(BaseState):
    def __init__(self, state_machine: Any) -> None:
        super().__init__(state_machine)
        
        has_records = settings.SAVE_MANAGER.exists("records")
        self.records = settings.SAVE_MANAGER.load("records") if has_records else {"workday": [], "arcade": []}
        
        self.fade_alpha = 255.0
        self.is_exiting = False
        
        self._setup_ui()
        
    def _setup_ui(self):
        from src.themes import BUTTON_THEME
        container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        
        btn_back = Button(
            settings.VIRTUAL_WIDTH / 2 - 50, settings.VIRTUAL_HEIGHT - 40,
            100, 25,
            tr("btn_back"),
            on_click=self.on_back_click,
            theme=BUTTON_THEME
        )
        container.add_child(btn_back)
        
        self.ui = UIManager(
            container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )
        
    def enter(self, enter_params=None):
        Timer.tween(0.5, [(self, {"fade_alpha": 0.0})])
        
    def on_back_click(self):
        if self.is_exiting: return
        settings.SOUNDS["press"].play()
        self.is_exiting = True
        
        def exit_to_title():
            self.state_machine.pop()
            self.state_machine.push(TitleScreenState(self.state_machine))
            
        Timer.tween(0.5, [(self, {"fade_alpha": 255.0})], on_finish=exit_to_title)

    def update(self, dt: float):
        self.ui.update(dt)

    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        surface.fill((20, 20, 30))
        
        render_text(
            surface,
            tr("records_title", default="Hall of Fame"),
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            20,
            (255, 220, 50),
            center=True,
            shadowed=True
        )
        
        # Workday records (Left)
        render_text(
            surface,
            tr("btn_workday"),
            settings.FONTS["minecraft"],
            settings.VIRTUAL_WIDTH * 0.25,
            50,
            (100, 255, 100),
            center=True
        )
        for i, rec in enumerate(self.records.get("workday", [])):
            text = tr("records_workday_format", default="{i}. {name} - Day {score}", i=i+1, name=rec["name"], score=rec["score"])
            render_text(
                surface, text, settings.FONTS["minecraft"],
                settings.VIRTUAL_WIDTH * 0.25, 70 + (i * 15),
                (255, 255, 255), center=True
            )
            
        # Arcade records (Right)
        render_text(
            surface,
            tr("btn_arcade"),
            settings.FONTS["minecraft"],
            settings.VIRTUAL_WIDTH * 0.75,
            50,
            (255, 200, 50),
            center=True
        )
        for i, rec in enumerate(self.records.get("arcade", [])):
            text = tr("records_arcade_format", default="{i}. {name} - {score} pts", i=i+1, name=rec["name"], score=rec["score"])
            render_text(
                surface, text, settings.FONTS["minecraft"],
                settings.VIRTUAL_WIDTH * 0.75, 70 + (i * 15),
                (255, 255, 255), center=True
            )
            
        self.ui.render(surface)
        
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
