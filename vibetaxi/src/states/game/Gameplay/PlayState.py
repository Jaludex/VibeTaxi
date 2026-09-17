from typing import Dict, Any, TypeVar
import math
import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.physics import BodyType
from gale.state import BaseState

import settings
from src.world.CityMap import CityMap
from src.entity.Taxi import Taxi
from src.gui.RadioTuner import Radio
from src.definitions.vehicles import VEHICLE_DEFS

class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.game_rule_strategy = enter_params.get("game_rule_strategy")
        if self.game_rule_strategy is None:
            # Fallback for testing if not provided
            from src.game_rules.ArcadeStrategy import ArcadeStrategy
            self.game_rule_strategy = ArcadeStrategy()
            
        self.city_map = enter_params.get("city_map")
        if self.city_map is None:
            self.city_map = CityMap("city")

        self.tilemap = self.city_map.tilemap

        self.taxi = enter_params.get("taxi")
        if self.taxi is None:
            spawn_x, spawn_y = self.city_map.get_taxi_spawn_position()
            self.taxi = Taxi(spawn_x, spawn_y, VEHICLE_DEFS["yellow_taxi"])

        self.taxi.tilemap = self.city_map.tilemap
        self.taxi.city_map = self.city_map
        self.taxi.set_physics(
            self.city_map.physics_world,
            body_type=BodyType.DYNAMIC,
            width=self.taxi.width,
            height=self.taxi.height,
        )

        self.camera = enter_params.get("camera")
        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.taxi, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.city_map.get_rect()
            self.camera.x, self.camera.y = self.taxi.x, self.taxi.y
            self.camera.update(0)

        self.taxi.camera = self.camera
        #radio
        self.radio =  enter_params.get("radio")
        if self.radio is None:
            self.radio = Radio(80, 296)
            
        self.active_passenger = None
        self.map_passengers = self.city_map.generate_passengers(spawn_chance=0.4)
        
        self.nearby_props = []
        self.nearby_passengers = []

        self.soundscape_channel = None
        try:
            soundscape = pygame.mixer.Sound(settings.BASE_DIR / "assets" / "music" / "city_soundscape.mp3")
            self.soundscape_channel = soundscape.play(loops=-1)
            if self.soundscape_channel:
                self.soundscape_channel.set_volume(0.5)
        except Exception as e:
            print("Error loading soundscape:", e)
            
        try:
            engine_start = settings.SOUNDS.get("engine_start")
            if engine_start:
                ch = engine_start.play()
                if ch: ch.set_volume(0.4)
        except Exception as e:
            pass
            
        self.taxi.init_sounds()
        self.exited = False

    def fixed_update(self) -> None:
        self.city_map.fixed_update()

    def update(self, dt):
        self.taxi.update(dt)
        self.city_map.update(dt, self.camera)
        self.camera.update(dt)
        self.radio.update(dt)
        
        self.game_rule_strategy.update(dt)
        
        if (self.taxi.health <= 0 or self.game_rule_strategy.game_over) and not getattr(self, "game_over_triggered", False):
            self.game_over_triggered = True
            from src.states.game.Gameplay.GameOverState import GameOverState
            self.state_machine.push(GameOverState(self.state_machine))
            return
        
        self.arrow_time = getattr(self, 'arrow_time', 0.0) + dt
        import math
        self.arrow_offset_y = (math.sin(self.arrow_time * 6.0) + 1.0) * 5.0
        
        if getattr(self, "_click_emitter", None) and getattr(self._click_emitter, "_is_emitting", False):
            import pygame
            from src.mouse_tools import physical_to_virtual
            px, py = pygame.mouse.get_pos()
            vx, vy = physical_to_virtual(px, py)
            if self.camera:
                world_x, world_y = self.camera.screen_to_world((vx, vy))
                self._click_emitter.x = world_x
                self._click_emitter.y = world_y
        
        if self.soundscape_channel:
            if self.radio.ind_song == 0:
                self.soundscape_channel.set_volume(0.5)
            else:
                self.soundscape_channel.set_volume(0.1)
        
        if self.camera:
            row_range, col_range = self.tilemap._visible_range(self.camera)
            
            def is_visible(x, y, margin_pixels):
                margin_cols = int(margin_pixels // self.tilemap.tile_width)
                margin_rows = int(margin_pixels // self.tilemap.tile_height)
                
                row, col = self.tilemap.tile_at(x, y)
                
                return (row_range.start - margin_rows <= row < row_range.stop + margin_rows) and \
                       (col_range.start - margin_cols <= col < col_range.stop + margin_cols)

            self.nearby_props = [
                prop for prop in self.city_map.props 
                if is_visible(prop.x, prop.y, margin_pixels=100)
            ]
            self.nearby_passengers = [
                p for p in self.map_passengers 
                if is_visible(p.x, p.y, margin_pixels=150)
            ]
        else:
            self.nearby_props = self.city_map.props[:]
            self.nearby_passengers = self.map_passengers[:]

        for p in self.nearby_passengers:
            p.update(dt)

        if self.active_passenger:
            self.update_active_passenger(dt)
        else:
            self.update_city_passengers(dt)
            
        # Vibe transitions
        is_vibe = type(self.taxi.state_machine.current).__name__ == "TaxiVibeState"
        was_vibe = getattr(self, "was_vibe", False)
        
        if not hasattr(self, "vibe_alpha"):
            self.vibe_alpha = 0.0
            self.vibe_color = None
            
        if is_vibe:
            genre = self.radio.get_current_genre()
            if genre and genre in settings.VIBE_COLORS:
                self.vibe_color = settings.VIBE_COLORS[genre]
            
        if is_vibe and not was_vibe:
            settings.SOUNDS["into_vibe"].play()
            from gale.timer import Timer
            Timer.tween(0.5, [(self, {"vibe_alpha": 40.0})])
        elif not is_vibe and was_vibe:
            settings.SOUNDS["out_vibe"].play()
            from gale.timer import Timer
            Timer.tween(0.5, [(self, {"vibe_alpha": 0.0})])
            
        self.was_vibe = is_vibe
            
    def update_active_passenger(self, dt: float):
        self.active_passenger.update(dt)

        if not self.active_passenger:
            return

        if self.active_passenger.is_walking():
            self.taxi.is_accelerating = False

        if self.active_passenger.is_riding():
            # Actualizar satisfacción
            current_genre = self.radio.get_current_genre()
            if current_genre == self.active_passenger.preferred_genre:
                self.active_passenger.satisfaction = min(100.0, self.active_passenger.satisfaction + 20.0 * dt)
            else:
                self.active_passenger.satisfaction = max(0.0, self.active_passenger.satisfaction - 15.0 * dt)
                
            from src.states.entity.TaxiVibeState import TaxiVibeState
            if self.active_passenger.satisfaction >= 100.0:
                if not isinstance(self.taxi.state_machine.current, TaxiVibeState):
                    self.taxi.state_machine.change("vibe")
            else:
                if isinstance(self.taxi.state_machine.current, TaxiVibeState):
                    self.taxi.state_machine.change("drive")

            dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
            dx = self.taxi.x - dest_x
            dy = self.taxi.y - dest_y
            distance = math.hypot(dx, dy)
            
            if distance <= 80 and abs(self.taxi.speed) < 5:
                # Capture variables for closure
                p = self.active_passenger
                distance_traveled = math.hypot(dest_x - p.pickup_x, dest_y - p.pickup_y)
                
                def reach_destination():
                    self.game_rule_strategy.on_passenger_delivered(distance_traveled)
                    self.active_passenger = None
                    
                    # Salir de vibe si estabamos ahi
                    from src.states.entity.TaxiVibeState import TaxiVibeState
                    if isinstance(self.taxi.state_machine.current, TaxiVibeState):
                        self.taxi.state_machine.change("drive")

                self.active_passenger.state_machine.change(
                    "walk", 
                    target=(dest_x, dest_y), 
                    on_arrival=reach_destination
                )

    def update_city_passengers(self, dt: float):
        for p in self.map_passengers:
            if p.is_waiting():
                dx = self.taxi.x - p.x
                dy = self.taxi.y - p.y
                distance = math.hypot(dx, dy)
                
                if distance <= settings.PASSENGER_DETECTION_RADIUS and abs(self.taxi.speed) < 5:
                    def reach_taxi():
                        p.state_machine.change("ride", taxi=self.taxi)
                    
                    p.state_machine.change("walk", target=self.taxi, on_arrival=reach_taxi)
                    self.active_passenger = p
                    self.map_passengers.remove(p)
                    
                    import random
                    genres = ["rock", "pop", "hiphop", "electronic", "jazz", None]
                    p.preferred_genre = random.choice(genres)
                    p.satisfaction = 10.0
                    p.pickup_x = p.x
                    p.pickup_y = p.y
                    print(f"DEBUG: Pasajero nuevo activo. Genero preferido: {p.preferred_genre if p.preferred_genre else 'off'}")
                    break

    def render(self, surface):
        self.city_map.render_layers(surface, self.camera, settings.TILED_GROUND_LAYERS)
        for emitter in self.city_map.particle_emitters:
            if getattr(emitter, "is_ground", False):
                emitter.render(surface, self.camera)

        render_active_passenger = False

        if self.active_passenger:
            if self.active_passenger.is_riding():
                dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
                self._render_detection_circle(surface, dest_x, dest_y, settings.PASSENGER_DELIVERY_RADIUS, settings.COLOR_PASSENGER_DELIVERY)
            
            if self.active_passenger.is_walking():
                render_active_passenger = True
        else:
            for p in self.nearby_passengers:
                if p.is_waiting():
                    self._render_detection_circle(surface, p.x, p.y, settings.PASSENGER_DETECTION_RADIUS, (255, 255, 0))

        self.city_map.render_layers(surface, self.camera, settings.TILED_MIDDLE_LAYERS)

        for prop in self.nearby_props:
            prop.render(surface, self.camera)
            
        for p in self.nearby_passengers:
            p.render(surface, self.camera)

        if render_active_passenger:
            self.active_passenger.render(surface, self.camera)
            
        self.city_map.render_traffic(surface, self.camera)
        self.taxi.render(surface, self.camera)
        for emitter in self.city_map.particle_emitters:
            if not getattr(emitter, "is_ground", False) and not getattr(emitter, "is_ui", False):
                emitter.render(surface, self.camera)

        self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_NO_SHADOW_LAYERS)
        self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_SHADOW_LAYERS)
        self.city_map.render_car_silhouette_if_obstructed(surface, self.taxi, self.camera)

        # Physics debug overlay
        try:
            if settings.PHYSICS_DEBUG:
                self.city_map.render_debug(surface, self.camera)
        except Exception:
            pass

        # Vibe filter
        vibe_alpha = getattr(self, "vibe_alpha", 0.0)
        vibe_color = getattr(self, "vibe_color", None)
        if vibe_alpha > 0 and vibe_color:
            filter_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            filter_surf.fill((*vibe_color, int(vibe_alpha)))
            surface.blit(filter_surf, (0, 0))

        self.radio.render(surface)
        
        if self.active_passenger and self.active_passenger.is_riding():
            dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
            self._render_arrow(surface, dest_x, dest_y)
            
        for emitter in self.city_map.particle_emitters:
            if getattr(emitter, "is_ui", False):
                emitter.render(surface, self.camera)
                
        if getattr(self.taxi, 'is_crashed', False):
            from gale.text import render_text
            render_text(
                surface,
                "GAME OVER - TAXI DESTROYED",
                settings.FONTS["minecraft"],
                settings.VIRTUAL_WIDTH // 2,
                settings.VIRTUAL_HEIGHT // 2,
                (255, 50, 50),
                center=True
            )
            
        self.game_rule_strategy.render_ui(surface, settings.FONTS["minecraft"], 20, 20)
        
    def _render_detection_circle(self, surface, x, y, radius, color):
        """Método auxiliar para renderizar los aros en el suelo con la cámara."""
        if self.camera:
            rect = self.camera.apply(pygame.Rect(x, y, 0, 0))
            px, py = rect.x, rect.y
        else:
            px, py = x, y
        pygame.draw.circle(surface, color, (px, py), radius, width=2)

    def _render_arrow(self, surface, dest_x, dest_y):
        arrow_tex = settings.TEXTURES.get("arrow")
        if not arrow_tex: return
        
        cam_x, cam_y = self.camera.offset
        cam_w, cam_h = settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT
        
        center_x = self.camera.x
        center_y = self.camera.y
        
        margin = 20
        if (cam_x + margin <= dest_x <= cam_x + cam_w - margin) and \
           (cam_y + margin <= dest_y <= cam_y + cam_h - margin):
            rotated_arrow = pygame.transform.rotate(arrow_tex, -90)
            rect = rotated_arrow.get_rect(center=(dest_x - cam_x, dest_y - cam_y - 40 + getattr(self, "arrow_offset_y", 0)))
            surface.blit(rotated_arrow, rect.topleft)
        else:
            import math
            dx = dest_x - center_x
            dy = dest_y - center_y
            angle = math.atan2(dy, dx)
            
            rotated_arrow = pygame.transform.rotate(arrow_tex, -math.degrees(angle))
            
            half_w = cam_w / 2 - 30
            half_h = cam_h / 2 - 30
            
            r_x = float('inf')
            if math.cos(angle) != 0:
                r_x = abs(half_w / math.cos(angle))
            r_y = float('inf')
            if math.sin(angle) != 0:
                r_y = abs(half_h / math.sin(angle))
                
            r = min(r_x, r_y)
            
            screen_pos_x = (cam_w / 2) + r * math.cos(angle)
            screen_pos_y = (cam_h / 2) + r * math.sin(angle)
            
            rect = rotated_arrow.get_rect(center=(screen_pos_x, screen_pos_y))
            surface.blit(rotated_arrow, rect.topleft)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.radio.on_input(input_id, input_data)
        self.taxi.on_input(input_id, input_data)

        if input_id == "mouse_click":
            import pygame
            from src.mouse_tools import physical_to_virtual
            from src.ParticleEmitter import ParticleEmitter
            if input_data.pressed:
                px, py = pygame.mouse.get_pos()
                vx, vy = physical_to_virtual(px, py)
                world_x, world_y = self.camera.screen_to_world((vx, vy))
                
                if getattr(self, "_click_emitter", None) is not None:
                    self._click_emitter.stop()
                    
                self._click_emitter = ParticleEmitter.create_mouse_click(world_x, world_y)
                self.city_map.particle_emitters.append(self._click_emitter)
            else:
                if getattr(self, "_click_emitter", None) is not None:
                    self._click_emitter.stop()
                    self._click_emitter = None

    def exit(self) -> None:
        self.exited = True
        if hasattr(self, 'soundscape_channel') and self.soundscape_channel:
            self.soundscape_channel.stop()
        if hasattr(self, 'taxi') and self.taxi:
            self.taxi.stop_sounds()
        pygame.mixer.music.stop()
