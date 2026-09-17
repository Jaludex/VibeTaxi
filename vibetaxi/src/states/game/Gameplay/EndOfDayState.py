from typing import Dict, Any
import pygame
from gale.input_handler import InputData
from gale.state import BaseState
from gale.timer import Timer
from gale.ui.manager import UIManager
from gale.ui.container import Container
from gale.ui.panel import Panel
from gale.ui.button import Button
from gale.ui.label import Label
from gale.ui.progress_bar import ProgressBar
from gale.ui.theme import Theme
# ImageWidget is probably not in gale.ui. Let's check how to draw an image

import settings
from src.game_rules.WorkdayStrategy import WorkdayStrategy
from src.definitions.vehicles import VEHICLE_DEFS

class EndOfDayState(BaseState):
    def __init__(self, state_machine, money, health, max_health, day):
        super().__init__(state_machine)
        self.money = money
        self.health = health
        self.max_health = max_health
        self.day = day
        self.alpha = 0
        self.ui = None

    def enter(self, **enter_params: Dict[str, Any]) -> None:
        if "win" in settings.SOUNDS:
            settings.SOUNDS["win"].play()
        
        Timer.tween(
            1.0,
            [(self, {"alpha": 180})],
            on_finish=self._setup_ui
        )

    def _get_health_color(self, health, max_health):
        pct = health / max_health
        if pct <= 0.2:
            return pygame.Color(255, 0, 0)
        elif pct <= 0.5:
            return pygame.Color(255, 255, 0)
        else:
            return pygame.Color(0, 255, 0)

    def _setup_ui(self):
        container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        
        panel_theme = Theme(
            background_color=pygame.Color(69, 40, 60),
            border_color=pygame.Color(255, 255, 255),
            border_width=2
        )
        
        panel_width = 300
        panel_height = 160
        panel = Panel(
            (settings.VIRTUAL_WIDTH - panel_width) // 2,
            (settings.VIRTUAL_HEIGHT - panel_height) // 2,
            panel_width,
            panel_height,
            theme=panel_theme
        )
        container.add_child(panel)

        # Labels
        lbl_theme = Theme(font=settings.FONTS["minecraft"], text_color=pygame.Color(255, 255, 255))
        day_label = Label(0, 10, f"End of Day {self.day}", theme=lbl_theme)
        day_label.x = panel.x + (panel.width - day_label.width) // 2
        day_label.y = panel.y + 10
        container.add_child(day_label)

        money_theme = Theme(font=settings.FONTS["minecraft"], text_color=pygame.Color(100, 255, 100))
        self.money_label = Label(0, 30, f"Money Earned: ${self.money:.2f}", theme=money_theme)
        self.money_label.x = panel.x + (panel.width - self.money_label.width) // 2
        self.money_label.y = panel.y + 30
        container.add_child(self.money_label)

        # Left side: Repair button
        repair_theme = Theme(
            font=settings.FONTS["minecraft"],
            background_color=pygame.Color(100, 60, 90),
            hover_color=pygame.Color(150, 90, 120),
            text_color=pygame.Color(255, 255, 255),
            border_color=pygame.Color(255, 255, 255),
            border_width=1
        )
        
        self.repair_button = Button(
            panel.x + 20,
            panel.y + 65,
            110, 30,
            f"Repair - ${settings.REPAIR_COST}",
            on_click=self._on_repair,
            theme=repair_theme
        )
        container.add_child(self.repair_button)
        self._update_repair_button()

        # Right side: Taxi and Progress Bar
        self.taxi_frame = settings.FRAMES["cars"][VEHICLE_DEFS["yellow_taxi"]["frame"]]
        base_taxi_image = pygame.Surface((self.taxi_frame.width, self.taxi_frame.height), pygame.SRCALPHA)
        base_taxi_image.blit(settings.TEXTURES["cars"], (0, 0), self.taxi_frame)
        
        # Rotate 90 degrees to be horizontal
        self.taxi_image = pygame.transform.rotate(base_taxi_image, -90)
        taxi_w = self.taxi_image.get_width()
        taxi_h = self.taxi_image.get_height()
        
        self.taxi_x = panel.x + 160 + (120 - taxi_w) // 2
        self.taxi_y = panel.y + 60
        
        progress_theme = Theme(
            background_color=pygame.Color(50, 50, 50),
            accent_color=self._get_health_color(self.health, self.max_health),
            border_color=pygame.Color(255, 255, 255),
            border_width=1
        )
        self.health_bar = ProgressBar(
            self.taxi_x, self.taxi_y + taxi_h + 5,
            taxi_w, 10,
            self.health,
            self.max_health,
            theme=progress_theme
        )
        container.add_child(self.health_bar)

        # Bottom buttons
        btn_width = 80
        btn_spacing = 10
        total_btn_width = (btn_width * 3) + (btn_spacing * 2)
        start_x = panel.x + (panel.width - total_btn_width) // 2
        
        btn_theme = Theme(
            font=settings.FONTS["minecraft"],
            background_color=pygame.Color(100, 60, 90),
            hover_color=pygame.Color(150, 90, 120),
            text_color=pygame.Color(255, 255, 255),
            border_color=pygame.Color(255, 255, 255),
            border_width=1
        )
        
        btn_exit = Button(
            start_x, panel.y + panel_height - 40,
            btn_width, 25,
            "Exit",
            on_click=self._on_exit,
            theme=btn_theme
        )
        container.add_child(btn_exit)

        btn_save = Button(
            start_x + btn_width + btn_spacing, panel.y + panel_height - 40,
            btn_width, 25,
            "Save & Exit",
            on_click=self._on_exit,
            theme=btn_theme
        )
        container.add_child(btn_save)

        btn_continue = Button(
            start_x + (btn_width + btn_spacing) * 2, panel.y + panel_height - 40,
            btn_width, 25,
            "Continue",
            on_click=self._on_continue,
            theme=btn_theme
        )
        container.add_child(btn_continue)

        self.ui = UIManager(
            container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )
        
    def _update_repair_button(self):
        if self.health >= self.max_health or self.money < settings.REPAIR_COST:
            self.repair_button.theme.background_color = (60, 40, 50)
            self.repair_button.theme.hover_color = (60, 40, 50)
            self.repair_button.theme.text_color = (150, 150, 150)
            self.repair_button.enabled = False
        else:
            self.repair_button.theme.background_color = (100, 60, 90)
            self.repair_button.theme.hover_color = (150, 90, 120)
            self.repair_button.theme.text_color = (255, 255, 255)
            self.repair_button.enabled = True

    def _on_repair(self):
        if self.health < self.max_health and self.money >= settings.REPAIR_COST:
            if "buy" in settings.SOUNDS: settings.SOUNDS["buy"].play()
            self.money -= settings.REPAIR_COST
            self.health = self.max_health
            
            # Update UI
            self.money_label.text = f"Money Earned: ${self.money:.2f}"
            self.health_bar.value = self.health
            self.health_bar.theme.accent_color = self._get_health_color(self.health, self.max_health)
            self._update_repair_button()
        else:
            if "error" in settings.SOUNDS: settings.SOUNDS["error"].play()

    def _on_exit(self):
        if "select" in settings.SOUNDS: settings.SOUNDS["select"].play()
        from src.states.game.Menus.TitleScreenState import TitleScreenState
        while len(self.state_machine.states) > 0:
            self.state_machine.pop()
        self.state_machine.push(TitleScreenState(self.state_machine))

    def _on_continue(self):
        if "select" in settings.SOUNDS: settings.SOUNDS["select"].play()
        self.ui = None # Disable UI interactions
        Timer.tween(
            1.0,
            [(self, {"alpha": 255})],
            on_finish=self._start_next_day
        )

    def _start_next_day(self):
        # We need to restart PlayState
        # Pop EndOfDayState and PlayState
        self.state_machine.pop() # Pop EndOfDayState
        self.state_machine.pop() # Pop PlayState
        
        # Push new PlayState
        from src.states.game.Gameplay.PlayState import PlayState
        self.state_machine.push(
            PlayState(self.state_machine),
            game_rule_strategy=WorkdayStrategy(money=self.money, day=self.day + 1),
            taxi_health=self.health
        )

    def update(self, dt: float) -> None:
        if self.ui:
            self.ui.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.alpha))
        surface.blit(overlay, (0, 0))

        if self.ui:
            self.ui.render(surface)
            if hasattr(self, 'taxi_image'):
                surface.blit(self.taxi_image, (self.taxi_x, self.taxi_y))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.ui:
            self.ui.on_input(input_id, input_data)
