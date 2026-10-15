from collections import OrderedDict
from typing import Any
import math
import pygame
import settings

# LRU Cache for rotated entity surfaces (e.g. vehicles)
_ROTATION_CACHE: OrderedDict = OrderedDict()
_ROTATION_CACHE_MAX: int = 512

def _get_rotated_surface(texture: pygame.Surface, frame: pygame.Rect, texture_id: str, frame_index: int, degrees: float) -> pygame.Surface:
    norm_deg = round(degrees % 360, 1)
    if norm_deg == 360.0:
        norm_deg = 0.0
    key = (texture_id, frame_index, norm_deg)
    
    cached = _ROTATION_CACHE.get(key)
    if cached is not None:
        _ROTATION_CACHE.move_to_end(key)
        return cached

    sub = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
    sub.blit(texture, (0, 0), frame)
    rotated = pygame.transform.rotate(sub, norm_deg)
    
    _ROTATION_CACHE[key] = rotated
    if len(_ROTATION_CACHE) > _ROTATION_CACHE_MAX:
        _ROTATION_CACHE.popitem(last=False)
        
    return rotated

class DrawableMixin:
    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        texture = settings.TEXTURES[self.texture_id]
        frame = settings.FRAMES[self.texture_id][self.frame_index]
        
        angle = getattr(self, "angle", None)
        flipped = getattr(self, "flipped", False)
        alpha = getattr(self, "alpha", 255)
        center_x, center_y = self.x, self.y
        
        has_rotation = False
        degrees = 0.0

        if angle is not None:
            try:
                center_x, center_y, degrees = self.get_render_center_and_degrees()
            except Exception:
                angle_offset = getattr(self, "angle_offset", 0)
                degrees = math.degrees(-angle) + angle_offset
                center_x, center_y = self.x, self.y
            
            norm_deg = round(degrees % 360, 1)
            if norm_deg not in (0.0, 360.0):
                has_rotation = True

        # Fast path: unrotated, un-flipped, full opacity (props, peds, etc.)
        if not has_rotation and not flipped and alpha >= 255:
            rect = pygame.Rect(0, 0, frame.width, frame.height)
            rect.center = (int(round(center_x)), int(round(center_y)))
            if camera is not None:
                rect = camera.apply(rect)
            surface.blit(texture, rect, frame)
            return

        # Rotated or alpha-blended path
        if has_rotation:
            image = _get_rotated_surface(texture, frame, self.texture_id, self.frame_index, degrees)
        else:
            image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
            image.fill((0, 0, 0, 0))
            image.blit(texture, (0, 0), frame)

        if flipped:
            image = pygame.transform.flip(image, True, False)

        if alpha < 255:
            try:
                tmp = image.copy()
                tmp.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
                image = tmp
            except Exception:
                image = image.copy()
                image.set_alpha(alpha)

        rect = image.get_rect(center=(int(round(center_x)), int(round(center_y))))
        if camera is not None:
            rect = camera.apply(rect)

        surface.blit(image, rect)