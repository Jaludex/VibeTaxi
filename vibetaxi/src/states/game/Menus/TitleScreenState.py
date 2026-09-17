import random
import math
import pygame
import settings

from typing import Dict, Any, Optional
from gale.camera import Camera
from gale.state import BaseState
from gale.timer import Timer
from gale.text import render_text

from src.world.CityMap import CityMap
from src.states.game.Gameplay.PlayState import PlayState


class TitleScreenState(BaseState):
    PHASE_FADE_IN = 0
    PHASE_PAN = 1
    PHASE_FADE_OUT = 2
    

    def enter(self, enter_params: Optional[Dict[str, Any]] = None):
        self._pan_phase = self.PHASE_FADE_IN
        self._scene_alpha: float = 255.0
        self._pan_timer = None
        self._pan_tween = None
        self._pan_duration: float = 6.0
        self._fade_duration: float = 1.0
        
        self.fade_alpha = 255.0
        self._scene_alpha = 255.0

        self.city_map = CityMap("city")
        self.city_map.muted = True

        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.camera.bounds = self.city_map.get_rect()

        self._positions = list(self.city_map.nodes.values())
        if not self._positions:
            rect = self.city_map.get_rect()
            self._positions = [
                (rect.width * 0.25, rect.height * 0.25),
                (rect.width * 0.75, rect.height * 0.25),
                (rect.width * 0.5, rect.height * 0.5),
                (rect.width * 0.25, rect.height * 0.75),
                (rect.width * 0.75, rect.height * 0.75),
            ]

        pos = random.choice(self._positions)
        self.camera.x, self.camera.y = pos
        self.camera.update(0)

        self._setup_ui()

        self.music_volume = 0.0
        menu_music = settings.MUSIC.get("menu")
        if menu_music:
            pygame.mixer.music.load(menu_music)
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1)

        self._fade_tween = Timer.tween(1.0, [(self, {"fade_alpha": 0.0, "music_volume": 0.5})])

        self._start_scene_fade_in()

    def _setup_ui(self):
        from gale.ui.manager import UIManager
        from gale.ui.button import Button
        from gale.ui.theme import Theme
        from gale.ui.container import Container

        container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        
        btn_theme = Theme(
            font=settings.FONTS["minecraft"],
            background_color=pygame.Color(100, 60, 90),
            hover_color=pygame.Color(150, 90, 120),
            text_color=pygame.Color(255, 255, 255),
            border_color=pygame.Color(255, 255, 255),
            border_width=1
        )
        disabled_theme = Theme(
            font=settings.FONTS["minecraft"],
            background_color=pygame.Color(60, 40, 50),
            hover_color=pygame.Color(60, 40, 50),
            text_color=pygame.Color(150, 150, 150),
            border_color=pygame.Color(150, 150, 150),
            border_width=1
        )

        center_y = settings.VIRTUAL_HEIGHT / 2 + 30
        
        btn_new_game = Button(
            settings.VIRTUAL_WIDTH / 2 - 160, center_y,
            150, 30,
            "New Game",
            on_click=self._on_new_game,
            theme=btn_theme
        )
        container.add_child(btn_new_game)
        
        has_save = settings.SAVE_MANAGER.exists("workday_save")
        if has_save:
            save_data = settings.SAVE_MANAGER.load("workday_save")
            day = save_data.get("day", 1)
            btn_resume = Button(
                settings.VIRTUAL_WIDTH / 2 + 10, center_y,
                150, 30,
                f"Resume Work. Day: {day}",
                on_click=self._on_resume,
                theme=btn_theme
            )
        else:
            btn_resume = Button(
                settings.VIRTUAL_WIDTH / 2 + 10, center_y,
                150, 30,
                "Resume Work",
                on_click=lambda: None,
                theme=disabled_theme
            )
            btn_resume.enabled = False
        
        container.add_child(btn_resume)
        
        # Records button
        has_records = settings.SAVE_MANAGER.exists("records")
        if has_records:
            records = settings.SAVE_MANAGER.load("records")
            if len(records.get("workday", [])) > 0 or len(records.get("arcade", [])) > 0:
                btn_records = Button(
                    settings.VIRTUAL_WIDTH / 2 - 50, center_y + 40,
                    100, 30,
                    "Records",
                    on_click=self._on_records,
                    theme=btn_theme
                )
                container.add_child(btn_records)
        
        self.ui = UIManager(
            container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )

    def _on_new_game(self):
        if not getattr(self, "mode_selection_triggered", False):
            settings.SOUNDS["press"].play()
            self.mode_selection_triggered = True
            self._cancel_pan_timers()
            from src.states.game.Menus.ModeSelectionState import ModeSelectionState
            self.state_machine.push(ModeSelectionState(self.state_machine))

    def _on_resume(self):
        if not getattr(self, "mode_selection_triggered", False):
            settings.SOUNDS["press"].play()
            self.mode_selection_triggered = True
            
            def proceed():
                self._cancel_pan_timers()
                save_data = settings.SAVE_MANAGER.load("workday_save")
                
                from src.game_rules.WorkdayStrategy import WorkdayStrategy
                strategy = WorkdayStrategy.load_dict(save_data)
                
                self.state_machine.pop() # TitleScreenState
                self.state_machine.push(PlayState(self.state_machine), game_rule_strategy=strategy, taxi_health=save_data.get("health"))

            Timer.tween(0.8, [(self, {"fade_alpha": 255.0})], ease_function_name="in_cubic", on_finish=proceed)

    def _on_records(self):
        if not getattr(self, "mode_selection_triggered", False):
            settings.SOUNDS["press"].play()
            from src.states.game.Menus.RecordsState import RecordsState
            self.state_machine.push(RecordsState(self.state_machine))

    def _pick_random_position(self):
        """Pick a random node position far from the current camera."""
        if len(self._positions) <= 1:
            return random.choice(self._positions)
        candidates = [
            p for p in self._positions
            if math.hypot(p[0] - self.camera.x, p[1] - self.camera.y) > 200
        ]
        if not candidates:
            candidates = self._positions
        return random.choice(candidates)

    def _start_scene_fade_in(self):
        """Fade the scene in from black, then start panning."""
        self._pan_phase = self.PHASE_FADE_IN
        self._cancel_pan_timers()
        self._scene_alpha = 255.0
        self._pan_tween = Timer.tween(
            self._fade_duration,
            [(self, {"_scene_alpha": 0.0})],
            on_finish=self._start_pan
        )

    def _start_pan(self):
        """Slowly pan the camera to a new position."""
        self._pan_phase = self.PHASE_PAN
        self._cancel_pan_timers()
        target = self._pick_random_position()
        self._pan_tween = Timer.tween(
            self._pan_duration,
            [(self.camera, {"x": target[0], "y": target[1]})],
            on_finish=self._start_scene_fade_out
        )

    def _start_scene_fade_out(self):
        """Fade to black, teleport camera, then fade in again."""
        self._pan_phase = self.PHASE_FADE_OUT
        self._cancel_pan_timers()
        self._pan_tween = Timer.tween(
            self._fade_duration,
            [(self, {"_scene_alpha": 255.0})],
            on_finish=self._on_scene_black
        )

    def _on_scene_black(self):
        """When fully black, teleport camera and start next cycle."""
        pos = self._pick_random_position()
        self.camera.x, self.camera.y = pos
        self.camera.update(0)
        self._start_scene_fade_in()

    def _cancel_pan_timers(self):
        if self._pan_tween:
            self._pan_tween.remove()
            self._pan_tween = None
        if self._pan_timer:
            self._pan_timer.remove()
            self._pan_timer = None

    def _toggle_prompt(self) -> None:
        pass

    def exit(self):
        self._cancel_pan_timers()
        if getattr(self, '_fade_tween', None):
            self._fade_tween.remove()
            self._fade_tween = None
        pygame.mixer.music.stop()

    def fixed_update(self) -> None:
        if self.city_map:
            self.city_map.fixed_update()

    def update(self, dt: float):
        if self.city_map and self.camera:
            self.city_map.update(dt, self.camera)
            self.camera.update(dt)
        pygame.mixer.music.set_volume(getattr(self, 'music_volume', 0.5))
        if hasattr(self, 'ui') and self.ui:
            self.ui.update(dt)

    def on_input(self, input_id, input_data):
        if hasattr(self, 'ui') and self.ui:
            self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface):
        surface.fill((20, 20, 30))

        # Render city background
        if self.city_map and self.camera:
            self.city_map.render_layers(surface, self.camera, settings.TILED_GROUND_LAYERS)
            self.city_map.render_layers(surface, self.camera, settings.TILED_MIDDLE_LAYERS)
            self.city_map.render_traffic(surface, self.camera)
            self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_NO_SHADOW_LAYERS)
            self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_SHADOW_LAYERS)

        # Scene fade overlay (for camera transitions)
        if self._scene_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self._scene_alpha)))))
            surface.blit(fade_surf, (0, 0))

        # Title gradient overlay
        gradient = settings.TEXTURES.get("title_gradient")
        if gradient:
            surface.blit(gradient, (0, 0))

        # Title
        render_text(
            surface,
            "Vibe Taxi",
            settings.FONTS["big"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2 - 40,
            (255, 220, 50),
            center=True,
            shadowed=True
        )

        if hasattr(self, 'ui') and self.ui:
            self.ui.render(surface)

        # Entry fade (from OpeningState transition)
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
