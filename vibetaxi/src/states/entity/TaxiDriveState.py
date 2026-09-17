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
            
        if type(self).__name__ == "TaxiDriveState":
            self.entity.is_drifting = False
            
        super().update(dt)