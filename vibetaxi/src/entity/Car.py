import math
import pygame
from src.entity.Entity import Entity

class Car(Entity):
    def __init__(self, x, y, definition):
        super().__init__(x, y, definition) 
        
        self.speed = 0
        self.angle = 0
        self.health = self.def_data["base_health"]
        
        self.max_speed = self.def_data["max_speed"]
        self.acceleration = self.def_data.get("acceleration", 500)
        self.friction = self.def_data.get("friction", 300)
        self.turn_speed = self.def_data.get("turn_speed", 4.0)
        
        self.target_x = x
        self.target_y = y

    def render_sprite(self, surface):
        car_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        car_surf.fill((255, 200, 0))
        pygame.draw.rect(car_surf, (50, 50, 50), (self.width - 15, 2, 10, self.height - 4))

        degrees = math.degrees(-self.angle)
        rotated_surf = pygame.transform.rotate(car_surf, degrees)
        rect = rotated_surf.get_rect(center=(self.x, self.y))
        
        surface.blit(rotated_surf, rect)