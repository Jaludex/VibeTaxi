from typing import Any
import math
import pygame
import settings

class DrawableMixin:
    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        texture = settings.TEXTURES[self.texture_id]
        frame = settings.FRAMES[self.texture_id][self.frame_index]
        
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        image.blit(texture, (0, 0), frame)

        angle = getattr(self, "angle", None)
        
        center_x, center_y = self.x, self.y

        if angle is not None:
            angle_offset = getattr(self, "angle_offset", 0)
            degrees = math.degrees(-angle) + angle_offset
            image = pygame.transform.rotate(image, degrees)

            pivot_x = getattr(self, "pivot_x", 0)
            pivot_y = getattr(self, "pivot_y", 0)
            
            if pivot_x != 0 or pivot_y != 0:
                offset = pygame.math.Vector2(pivot_x, pivot_y)
                rotated_offset = offset.rotate(-degrees)
                
                center_x = (self.x + pivot_x) - rotated_offset.x
                center_y = (self.y + pivot_y) - rotated_offset.y

        elif getattr(self, "flipped", False):
            image = pygame.transform.flip(image, True, False)

        alpha = getattr(self, "alpha", 255)
        if alpha < 255:
            image.set_alpha(alpha)

        rect = image.get_rect(center=(center_x, center_y))

        if camera is not None:
            rect = camera.apply(rect)

        surface.blit(image, rect)