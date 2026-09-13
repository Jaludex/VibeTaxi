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
        if angle is not None:
            degrees = math.degrees(-angle) - 90
            image = pygame.transform.rotate(image, degrees)
        elif getattr(self, "flipped", False):
            image = pygame.transform.flip(image, True, False)

        rect = image.get_rect(center=(self.x, self.y))

        if camera is not None:
            rect = camera.apply(rect)

        surface.blit(image, rect)