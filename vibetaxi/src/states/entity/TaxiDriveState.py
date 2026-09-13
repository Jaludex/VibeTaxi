import pygame
from src.states.entity.CarDriveState import CarDriveState
from src.mouse_tools import physical_to_virtual
from src import commands

class TaxiDriveState(CarDriveState):
    def update(self, dt):
        px, py = pygame.mouse.get_pos()
        
        vx, vy = physical_to_virtual(px, py)
        
        camera = getattr(self.entity, "camera", None)
        if camera:
            self.entity.target_x, self.entity.target_y = camera.screen_to_world((vx, vy))
        else:
            self.entity.target_x, self.entity.target_y = vx, vy
        
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
        elif input_id == "reverse":
            if input_data.pressed:
                commands.REVERSE.execute(self.entity)
            else:
                commands.STOP_REVERSE.execute(self.entity)