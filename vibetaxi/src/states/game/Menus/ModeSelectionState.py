import pygame
import settings
from typing import Dict, Any, Optional
from gale.state import BaseState
from gale.timer import Timer
from gale.ui.manager import UIManager
from gale.ui.button import Button
from gale.ui.label import Label
from gale.ui.window import Window
from gale.ui.container import Container

from src.states.game.Gameplay.PlayState import PlayState
from src.game_rules.WorkdayStrategy import WorkdayStrategy
from src.game_rules.ArcadeStrategy import ArcadeStrategy

class ModeSelectionState(BaseState):
    def __init__(self, state_machine: Any) -> None:
        super().__init__(state_machine)
        self.fade_alpha = 0.0
        
        window_width = 340
        window_height = 240
        window_x = settings.VIRTUAL_WIDTH / 2 - window_width / 2
        
        self.panel_y = settings.VIRTUAL_HEIGHT + 100
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - window_height / 2
        
        self.is_exiting = False
        self.selected_mode = None
        self._last_panel_y = self.panel_y
        
        # We will manually calculate widget positions relative to the window
        self.btn_jornada = Button(
            window_x + 60,
            self.panel_y + 180,
            100, 30,
            "Jornada",
            on_click=lambda: self.select_mode("jornada")
        )
        
        self.btn_arcade = Button(
            window_x + 180,
            self.panel_y + 180,
            100, 30,
            "Arcade",
            on_click=lambda: self.select_mode("arcade")
        )
        
        self.desc_label = Label(
            settings.VIRTUAL_WIDTH / 2,
            self.panel_y + 145,
            "Elige un modo de juego.",
            center=True
        )
        
        self.window = Window(
            window_x, 
            self.panel_y, 
            window_width, window_height,
            title="Selecciona un Modo",
            on_close=self.on_close_click,
            children=[self.btn_jornada, self.btn_arcade, self.desc_label]
        )
        
        self.container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[self.window])
        self.ui = UIManager(
            self.container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )
        
    def enter(self, enter_params: Optional[Dict[str, Any]] = None):
        self.fade_alpha = 0.0
        self.panel_y = settings.VIRTUAL_HEIGHT + 100
        dy = self.panel_y - self._last_panel_y
        if dy != 0:
            for child in self.container.children:
                self._offset_widget(child, dy)
        self._last_panel_y = self.panel_y
        self.is_exiting = False
        
        Timer.tween(1.0, [(self, {"fade_alpha": 180.0})])
        Timer.tween(1.0, [(self, {"panel_y": self.target_y})])
        
    def _offset_widget(self, w, dy):
        w.y += dy
        if hasattr(w, "children"):
            for c in w.children:
                self._offset_widget(c, dy)
        
    def update_ui_y(self):
        dy = self.panel_y - self._last_panel_y
        if dy != 0:
            for child in self.container.children:
                self._offset_widget(child, dy)
            self._last_panel_y = self.panel_y
            
    def select_mode(self, mode):
        if self.is_exiting: return
        self.selected_mode = mode
        self.is_exiting = True
        Timer.tween(0.8, [(self, {"fade_alpha": 255.0})], on_finish=self.start_game)
            
    def on_close_click(self):
        if self.is_exiting: return
        self.is_exiting = True
        # Window.close() sets visible to False, we want to animate it out while visible!
        self.window.visible = True
        
        # Animate out and return to Title
        Timer.tween(0.8, [
            (self, {"fade_alpha": 0.0}),
            (self, {"panel_y": settings.VIRTUAL_HEIGHT + 100})
        ], on_finish=self.return_to_title)
        
    def return_to_title(self):
        self.state_machine.pop() # Pop ModeSelectionState
        # Reset flag in TitleScreenState so it can be opened again
        if len(self.state_machine.states) > 0:
            self.state_machine.states[-1].mode_selection_triggered = False
        
    def start_game(self):
        self.state_machine.pop() # Pops ModeSelectionState
        self.state_machine.pop() # Pops TitleScreenState
        
        if self.selected_mode == "jornada":
            strategy = WorkdayStrategy()
        else:
            strategy = ArcadeStrategy()
            
        self.state_machine.push(PlayState(self.state_machine), game_rule_strategy=strategy)

    def update(self, dt: float):
        self.update_ui_y()
        self.ui.update(dt)
        
        # Update description text based on hover
        if self.btn_jornada.hovered:
            self.desc_label.set_text("Gana dinero para reparar tu auto.")
        elif self.btn_arcade.hovered:
            self.desc_label.set_text("Gana tiempo con cada entrega.")
        else:
            self.desc_label.set_text("Elige un modo de juego.")

    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
            
        self.ui.render(surface)
        
        # Placeholder for image
        img_rect_y = self.panel_y + 40
        img_rect_x = settings.VIRTUAL_WIDTH / 2 - 100
        pygame.draw.rect(surface, (50, 50, 60), (img_rect_x, img_rect_y, 200, 90))
        
        # Exit fade (to black, used for start_game)
        if self.fade_alpha > 180.0 and self.selected_mode and self.is_exiting and self.target_y == self.panel_y:
            top_alpha = (self.fade_alpha - 180.0) / (255.0 - 180.0) * 255.0
            top_fade = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            top_fade.fill((0, 0, 0, int(max(0.0, min(255.0, top_alpha)))))
            surface.blit(top_fade, (0, 0))
