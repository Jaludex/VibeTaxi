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

    def fixed_update(self) -> None:
        self.city_map.fixed_update()

    def update(self, dt):
        self.taxi.update(dt)
        self.city_map.update(dt, self.camera)
        self.camera.update(dt)
        self.radio.update(dt)
        
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
            
    def update_active_passenger(self, dt: float):
        self.active_passenger.update(dt)

        if not self.active_passenger:
            return

        if self.active_passenger.is_walking():
            self.taxi.is_accelerating = False

        if self.active_passenger.is_riding():
            dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
            dx = self.taxi.x - dest_x
            dy = self.taxi.y - dest_y
            distance = math.hypot(dx, dy)
            
            if distance <= 80 and abs(self.taxi.speed) < 5:
                def reach_destination():
                    self.active_passenger = None

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
            if not getattr(emitter, "is_ground", False):
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

        self.radio.render(surface)
        
    def _render_detection_circle(self, surface, x, y, radius, color):
        """Método auxiliar para renderizar los aros en el suelo con la cámara."""
        if self.camera:
            rect = self.camera.apply(pygame.Rect(x, y, 0, 0))
            px, py = rect.x, rect.y
        else:
            px, py = x, y
        pygame.draw.circle(surface, color, (px, py), radius, width=2)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.radio.on_input(input_id, input_data)
        self.taxi.on_input(input_id, input_data)
