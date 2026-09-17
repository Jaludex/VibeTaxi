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
            # Prefer entity-provided helper to compute center and degrees so
            # the rendering and collision overlay match exactly
            try:
                center_x, center_y, degrees = self.get_render_center_and_degrees()
            except Exception:
                angle_offset = getattr(self, "angle_offset", 0)
                degrees = math.degrees(-angle) + angle_offset
                center_x, center_y = self.x, self.y

            image = pygame.transform.rotate(image, degrees)

            pivot_x = getattr(self, "pivot_x", 0)
            pivot_y = getattr(self, "pivot_y", 0)
            
            # center_x/center_y already computed above (including pivot)

        elif getattr(self, "flipped", False):
            image = pygame.transform.flip(image, True, False)

        alpha = getattr(self, "alpha", 255)
        if alpha < 255:
            # Multiply alpha into per-pixel alpha to avoid black borders after rotate
            try:
                tmp = image.copy()
                tmp.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
                image = tmp
            except Exception:
                # Fallback
                image.set_alpha(alpha)

        rect = image.get_rect(center=(center_x, center_y))

        if camera is not None:
            rect = camera.apply(rect)

        surface.blit(image, rect)