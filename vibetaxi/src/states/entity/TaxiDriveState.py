import pygame
from src.states.entity.CarDriveState import CarDriveState
from src.mouse_tools import physical_to_virtual
from src import commands

class TaxiDriveState(CarDriveState):
    def update(self, dt):
        strategy = getattr(self.entity, "input_strategy", None)
        if not strategy:
            from src.input_strategies import MouseInputStrategy
            strategy = MouseInputStrategy()
            self.entity.input_strategy = strategy
        self.entity.target_x, self.entity.target_y = strategy.get_target_position(self.entity, dt)
            
        if type(self).__name__ == "TaxiDriveState":
            self.entity.is_drifting = False
            
        super().update(dt)