import pygame

from gale.state import BaseState

from src.entity.Taxi import Taxi
from src.definitions.vehicles import VEHICLE_DEFS




class PlayState(BaseState):
    def enter(self, **kwargs):
        self.taxi = Taxi(400, 300, VEHICLE_DEFS["yellow_taxi"])

    def update(self, dt):
        self.taxi.update(dt)

    def render(self, surface):
        #Temp
        surface.fill((50, 50, 50))

        self.taxi.render(surface)

    def on_input(self, input_id, input_data):
        self.taxi.on_input(input_id, input_data)