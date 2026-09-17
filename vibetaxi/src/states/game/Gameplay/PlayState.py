from typing import Dict, Any, TypeVar
import math
import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState

import settings
from src.world.CityMap import CityMap
from src.entity.Taxi import Taxi
from src.gui.RadioTuner import Radio
from src.definitions.vehicles import VEHICLE_DEFS
from src.gui.PassengerHUD import PassengerHUD
from gale.ui.manager import UIManager
from gale.timer import Timer

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
        #radio
        self.radio =  enter_params.get("radio")
        if self.radio is None:
            self.radio = Radio(80, 296)
            
        self.active_passenger = None
        
        self.map_passengers = self.city_map.generate_passengers(spawn_chance=0.4)
        
        self.passenger_hud = PassengerHUD()
        self.ui = UIManager(
            self.passenger_hud.container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )

    def update(self, dt):
        self.city_map.update(dt)
        self.taxi.update(dt)
        self.passenger_hud.update(dt)
        self.ui.update(dt)
        self.camera.update(dt)
        self.radio.update(dt)
        Timer.update(dt)
        
        
        for prop in self.city_map.props:
            if prop.collidable and self.taxi.collides(prop):
                prop.on_collide(self.taxi)
                self.taxi.speed *= 0.5
                if self.active_passenger and self.active_passenger.is_riding():
                    self.active_passenger.on_collision(self.passenger_hud)
        
        for p in self.map_passengers:
            p.update(dt)

        if self.active_passenger:
            self.update_active_passenger(dt)
        else:
            self.update_city_passengers(dt)
            

    def update_active_passenger(self, dt: float):
        self.active_passenger.update(dt)

        if not self.active_passenger:
            return

        if self.active_passenger.is_riding():
            song_actual = self.radio.get_current_song()
            self.active_passenger.update_comfort(dt, song_actual, self.passenger_hud)
            
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
                self.passenger_hud.unbind_passenger()

    def update_city_passengers(self, dt: float):
        for p in self.map_passengers:
            if p.is_waiting():
                dx = self.taxi.x - p.x
                dy = self.taxi.y - p.y
                distance = math.hypot(dx, dy)
                
                if distance <= settings.PASSENGER_DETECTION_RADIUS and abs(self.taxi.speed) < 5:
                    def reach_taxi():
                        p.state_machine.change("ride", taxi=self.taxi)
                        self.passenger_hud.bind_passenger(p)
                    
                    p.state_machine.change("walk", target=self.taxi, on_arrival=reach_taxi)
                    self.active_passenger = p
                    self.map_passengers.remove(p)
                    break

    def render(self, surface):
        self.city_map.render_layers(surface, self.camera, settings.TILED_GROUND_LAYERS)

        if self.active_passenger:
            if self.active_passenger.is_riding():
                dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
                self._render_detection_circle(surface, dest_x, dest_y, settings.PASSENGER_DELIVERY_RADIUS, (0, 255, 0))
            if self.active_passenger.is_walking():
                self.active_passenger.render(surface, self.camera)
        else:
            for p in self.map_passengers:
                self._render_detection_circle(surface, p.x, p.y, settings.PASSENGER_DETECTION_RADIUS, (255, 255, 0))

        self.city_map.render_layers(surface, self.camera, settings.TILED_MIDDLE_LAYERS)

        for prop in self.city_map.props:
            prop.render(surface, self.camera)
            
        for p in self.map_passengers:
            p.render(surface, self.camera)
            
        self.taxi.render(surface, self.camera)
        
        self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_LAYERS)
        self.city_map.render_car_silhouette_if_obstructed(surface, self.taxi, self.camera)
        self.radio.render(surface)
        self.ui.render(surface)
        
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
        self.ui.on_input(input_id, input_data)
