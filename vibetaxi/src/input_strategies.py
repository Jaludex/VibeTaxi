import pygame
import math
import settings
from src.mouse_tools import physical_to_virtual

class MouseInputStrategy:
    def get_target_position(self, entity, dt):
        px, py = pygame.mouse.get_pos()
        vx, vy = physical_to_virtual(px, py)
        camera = getattr(entity, "camera", None)
        if camera:
            return camera.screen_to_world((vx, vy))
        return vx, vy

class KeyboardInputStrategy:
    def get_target_position(self, entity, dt):
        dx = 0
        dy = 0
        if getattr(entity, "key_up", False): dy -= 1
        if getattr(entity, "key_down", False): dy += 1
        if getattr(entity, "key_left", False): dx -= 1
        if getattr(entity, "key_right", False): dx += 1
        
        if dx == 0 and dy == 0:
            entity.is_accelerating = False
            return entity.x, entity.y
            
        entity.is_accelerating = True
        angle = math.atan2(dy, dx)
        max_dist = getattr(settings, 'MOUSE_MAX_SPEED_RADIUS', 80)
        return entity.x + math.cos(angle) * max_dist, entity.y + math.sin(angle) * max_dist

class GamepadInputStrategy:
    def get_target_position(self, entity, dt):
        dx = getattr(entity, "steer_x", 0.0)
        dy = getattr(entity, "steer_y", 0.0)
        
        # Deadzone to prevent stick drift
        deadzone = getattr(settings, 'GAMEPAD_DEADZONE', 0.25)
        if abs(dx) < deadzone: dx = 0
        if abs(dy) < deadzone: dy = 0
        
        if dx == 0 and dy == 0:
            entity.is_accelerating = False
            return entity.x, entity.y
            
        entity.is_accelerating = True
        dist_ratio = math.hypot(dx, dy)
        if dist_ratio > 1.0: dist_ratio = 1.0
        
        angle = math.atan2(dy, dx)
        max_dist = getattr(settings, 'MOUSE_MAX_SPEED_RADIUS', 80)
        return entity.x + math.cos(angle) * max_dist * dist_ratio, entity.y + math.sin(angle) * max_dist * dist_ratio

