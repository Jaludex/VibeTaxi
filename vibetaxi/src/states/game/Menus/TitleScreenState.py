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
        self.show_prompt: bool = True

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

        self._blink_timer = Timer.every(0.6, self._toggle_prompt)

        self.music_volume = 0.0
        menu_music = settings.MUSIC.get("menu")
        if menu_music:
            pygame.mixer.music.load(menu_music)
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1)

        self._fade_tween = Timer.tween(1.0, [(self, {"fade_alpha": 0.0, "music_volume": 0.5})])

        self._start_scene_fade_in()

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
        self.show_prompt = not self.show_prompt

    def exit(self):
        self._cancel_pan_timers()
        if self._blink_timer:
            self._blink_timer.remove()
            self._blink_timer = None
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

    def on_input(self, input_id, input_data):
        if input_id == "mouse_click" and input_data.pressed:
            if not getattr(self, "mode_selection_triggered", False):
                settings.SOUNDS["press"].play()
                self.mode_selection_triggered = True
                self._cancel_pan_timers()
                from src.states.game.Menus.ModeSelectionState import ModeSelectionState
                self.state_machine.push(ModeSelectionState(self.state_machine))

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
            settings.VIRTUAL_HEIGHT / 2 - 20,
            (255, 220, 50),
            center=True,
            shadowed=True
        )

        # Prompt
        if self.show_prompt:
            render_text(
                surface,
                "Haz clic para comenzar",
                settings.FONTS["minecraft"],
                settings.VIRTUAL_WIDTH / 2,
                settings.VIRTUAL_HEIGHT / 2 + 30,
                (255, 255, 255),
                center=True
            )

        # Entry fade (from OpeningState transition)
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
