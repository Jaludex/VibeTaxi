import pygame
from typing import Any

class CollidableMixin:
    def get_collision_rect(self) -> pygame.Rect:
        c_width = getattr(self, "collision_width", self.width)
        c_height = getattr(self, "collision_height", self.height)
        return pygame.Rect(
            round(self.x - c_width / 2), 
            round(self.y - c_height / 2), 
            c_width, 
            c_height
        )

    def collides(self, another: Any) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())