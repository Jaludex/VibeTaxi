import pygame
from src.states.entity.CarDriveState import CarDriveState
from src.mouse_tools import physical_to_virtual
from src import commands

class TaxiDriveState(CarDriveState):
    def update(self, dt):
        px, py = pygame.mouse.get_pos()
        self.entity.target_x, self.entity.target_y = physical_to_virtual(px, py)
        super().update(dt)

    def on_input(self, input_id, input_data):
        if input_id == "mouse_click":
            if input_data.pressed:
                commands.ACCELERATE.execute(self.entity)
            else:
                commands.STOP_ACCELERATE.execute(self.entity)
        elif input_id == "brake":
            if input_data.pressed:
                commands.BRAKE.execute(self.entity)
            else:
                commands.STOP_BRAKE.execute(self.entity)