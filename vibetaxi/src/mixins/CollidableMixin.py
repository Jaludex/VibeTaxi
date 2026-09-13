import pygame
from typing import Any

class CollidableMixin:
    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x - self.width / 2), 
            round(self.y - self.height / 2), 
            self.width, 
            self.height
        )

    def collides(self, another: Any) -> bool:
        return self.get_collision_rect().colliderect(another.get_collision_rect())