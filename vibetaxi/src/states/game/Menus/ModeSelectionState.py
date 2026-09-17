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
from src.game_rules.ZenStrategy import ZenStrategy

from src.game_rules.TutorialStrategy import TutorialStrategy
from src.states.game.Gameplay.TutorialPlayState import TutorialPlayState

class ModeSelectionState(BaseState):
    def __init__(self, state_machine: Any) -> None:
        super().__init__(state_machine)
        self.fade_alpha = 0.0
        
        window_width = 460
        window_height = 120
        window_x = settings.VIRTUAL_WIDTH / 2 - window_width / 2
        
        self.panel_y = settings.VIRTUAL_HEIGHT + 100
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - window_height / 2
        
        self.is_exiting = False
        self.selected_mode = None
        self._last_panel_y = self.panel_y
        
        # We will manually calculate widget positions relative to the window
        self.btn_tutorial = Button(
            window_x + 20,
            self.panel_y + 75,
            95, 30,
            "Tutorial",
            on_click=lambda: self.select_mode("tutorial")
        )
        
        self.btn_jornada = Button(
            window_x + 130,
            self.panel_y + 75,
            95, 30,
            "Workday",
            on_click=lambda: self.select_mode("workday")
        )
        
        self.btn_arcade = Button(
            window_x + 240,
            self.panel_y + 75,
            95, 30,
            "Arcade",
            on_click=lambda: self.select_mode("arcade")
        )

        self.btn_zen = Button(
            window_x + 350,
            self.panel_y + 75,
            95, 30,
            "Zen",
            on_click=lambda: self.select_mode("zen")
        )
        
        self.desc_label = Label(
            settings.VIRTUAL_WIDTH / 2,
            self.panel_y + 45,
            "Choose a game mode",
            center=True
        )
        
        self.window = Window(
            window_x, 
            self.panel_y, 
            window_width, window_height,
            title="Please select a mode",
            on_close=self.on_close_click,
            children=[self.btn_tutorial, self.btn_jornada, self.btn_arcade, self.btn_zen, self.desc_label]
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
        
        Timer.tween(1.0, [(self, {"fade_alpha": 180.0, "panel_y": self.target_y})], ease_function_name="out_cubic")
        
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
        settings.SOUNDS["press"].play()
        self.selected_mode = mode
        self.is_exiting = True
        Timer.tween(0.8, [(self, {"fade_alpha": 255.0})], ease_function_name="in_cubic", on_finish=self.start_game)
            
    def on_close_click(self):
        if self.is_exiting: return
        settings.SOUNDS["press"].play()
        self.is_exiting = True
        # Window.close() sets visible to False, we want to animate it out while visible!
        self.window.visible = True
        
        # Animate out and return to Title
        Timer.tween(0.8, [
            (self, {"fade_alpha": 0.0}),
            (self, {"panel_y": settings.VIRTUAL_HEIGHT + 100})
        ], ease_function_name="in_cubic", on_finish=self.return_to_title)
        
    def return_to_title(self):
        self.state_machine.pop() # Pop ModeSelectionState
        # Reset flag in TitleScreenState so it can be opened again
        if len(self.state_machine.states) > 0:
            self.state_machine.states[-1].mode_selection_triggered = False
        
    def start_game(self):
        self.state_machine.pop() # Pops ModeSelectionState
        self.state_machine.pop() # Pops TitleScreenState
        
        if self.selected_mode == "workday":
            strategy = WorkdayStrategy()
            self.state_machine.push(PlayState(self.state_machine), game_rule_strategy=strategy)
        elif self.selected_mode == "arcade":
            strategy = ArcadeStrategy()
            self.state_machine.push(PlayState(self.state_machine), game_rule_strategy=strategy)
        elif self.selected_mode == "zen":
            strategy = ZenStrategy()
            self.state_machine.push(PlayState(self.state_machine), game_rule_strategy=strategy)
        else: # tutorial
            strategy = TutorialStrategy()
            self.state_machine.push(TutorialPlayState(self.state_machine), game_rule_strategy=strategy)

    def update(self, dt: float):
        self.update_ui_y()
        self.ui.update(dt)
        
        # Update description text based on hover
        if self.btn_tutorial.hovered:
            self.desc_label.set_text("Learn the basics of the game")
        elif self.btn_jornada.hovered:
            self.desc_label.set_text("Win money with each trip. Use it to repare your car")
        elif self.btn_arcade.hovered:
            self.desc_label.set_text("Win as many trips as you can before time runs out")
        elif self.btn_zen.hovered:
            self.desc_label.set_text("No damage, no limits. Just chill and drive.")
        else:
            self.desc_label.set_text("Choose a game mode.")

    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
            
        self.ui.render(surface)
        
        # Exit fade (to black, used for start_game)
        if self.fade_alpha > 180.0 and self.selected_mode and self.is_exiting and self.target_y == self.panel_y:
            top_alpha = (self.fade_alpha - 180.0) / (255.0 - 180.0) * 255.0
            top_fade = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            top_fade.fill((0, 0, 0, int(max(0.0, min(255.0, top_alpha)))))
            surface.blit(top_fade, (0, 0))
