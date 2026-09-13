from typing import Dict, Any
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

        self.camera = enter_params.get("camera")
        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.taxi, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.city_map.get_rect()
            self.camera.x, self.camera.y = self.taxi.x, self.taxi.y
            self.camera.update(0)

        self.taxi.camera = self.camera

    def update(self, dt: float) -> None:
        self.taxi.update(dt)
        self.city_map.update(dt)
        self.camera.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.city_map.render(surface, self.camera)
        self.taxi.render(surface, self.camera)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.taxi.on_input(input_id, input_data)