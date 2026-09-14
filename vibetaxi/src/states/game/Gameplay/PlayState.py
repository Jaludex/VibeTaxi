from typing import Dict, Any
import math
import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState

import settings
from src.world.CityMap import CityMap
from src.entity.Taxi import Taxi
from src.definitions.vehicles import VEHICLE_DEFS

class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.city_map = enter_params.get("city_map")
        if self.city_map is None:
            self.city_map = CityMap("city")

        self.tilemap = self.city_map.tilemap

        self.taxi = enter_params.get("taxi")
        if self.taxi is None:
            self.taxi = Taxi(400, 300, VEHICLE_DEFS["yellow_taxi"])

        self.taxi.tilemap = self.city_map.tilemap

        self.camera = enter_params.get("camera")
        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.taxi, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.city_map.get_rect()
            self.camera.x, self.camera.y = self.taxi.x, self.taxi.y
            self.camera.update(0)

        self.taxi.camera = self.camera

        self.active_passenger = None
        
        self.map_passengers = self.city_map.generate_passengers(spawn_chance=0.4)

    def update(self, dt):
        self.city_map.update(dt)
        self.taxi.update(dt)

        self.camera.update(dt)
        
        for prop in self.city_map.props:
            if prop.collidable and self.taxi.collides(prop):
                prop.on_collide(self.taxi)
                self.taxi.speed *= 0.5
        
        for p in self.map_passengers:
            p.update(dt)

        if not self.active_passenger:
            for p in self.map_passengers:
                if p.state == "waiting":
                    dx = self.taxi.x - p.x
                    dy = self.taxi.y - p.y
                    distance = math.hypot(dx, dy)
                    
                    if distance <= p.radius and abs(self.taxi.speed) < 5:
                        p.state = "entering"
                        p.target_taxi = self.taxi
                        p.change_animation("walk")
                        
                        self.active_passenger = p
                        self.map_passengers.remove(p)
                        break
                        
        else:
            if self.active_passenger.state == "entering":
                self.active_passenger.update(dt)
                if self.active_passenger.state == "riding":
                    pass
            elif self.active_passenger.state == "riding":
                dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
                dx = self.taxi.x - dest_x
                dy = self.taxi.y - dest_y
                distance = math.hypot(dx, dy)
                
                # Si el taxi llega al destino y está detenido
                if distance <= settings.PASSENGER_DELIVERY_RADIUS and abs(self.taxi.speed) < 5:
                    self.active_passenger.x = self.taxi.x
                    self.active_passenger.y = self.taxi.y
                    self.active_passenger.state = "leaving"
                    self.active_passenger.target_dest_pos = (dest_x, dest_y)
                    self.active_passenger.change_animation("walk")
                
            elif self.active_passenger.state == "leaving":
                self.active_passenger.update(dt)
                if self.active_passenger.state == "done":
                    self.active_passenger = None

    def render(self, surface):
        # 1. Suelo
        self.city_map.render_layers(surface, self.camera, settings.TILED_GROUND_LAYERS)

        if not self.active_passenger:
            for p in self.map_passengers:
                self._render_detection_circle(surface, p.x, p.y, p.radius, (255, 255, 0))
                
        if self.active_passenger:
            if self.active_passenger.state == "riding":
                dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
                self._render_detection_circle(surface, dest_x, dest_y, settings.PASSENGER_DELIVERY_RADIUS, (0, 255, 0))

            elif self.active_passenger.state == "entering" or self.active_passenger.state == "leaving":
                self.active_passenger.render(surface, self.camera)
        else:
            for p in self.map_passengers:
                self._render_detection_circle(surface, p.x, p.y, p.radius, (255, 255, 0))

        self.city_map.render_layers(surface, self.camera, settings.TILED_MIDDLE_LAYERS)

        for prop in self.city_map.props:
            prop.render(surface, self.camera)
            
        for p in self.map_passengers:
            p.render(surface, self.camera)
            
        if self.active_passenger and self.active_passenger.state == "entering":
            self.active_passenger.render(surface, self.camera)
            
        self.taxi.render(surface, self.camera)
        
        self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_LAYERS)
        self.city_map.render_car_silhouette_if_obstructed(surface, self.taxi, self.camera)

    def _render_detection_circle(self, surface, x, y, radius, color):
        """Método auxiliar para renderizar los aros en el suelo con la cámara."""
        if self.camera:
            rect = self.camera.apply(pygame.Rect(x, y, 0, 0))
            px, py = rect.x, rect.y
        else:
            px, py = x, y
        pygame.draw.circle(surface, color, (px, py), radius, width=2)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.taxi.on_input(input_id, input_data)