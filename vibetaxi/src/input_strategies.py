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

    def get_binding_texts(self) -> dict:
        from src.i18n import tr
        return {
            "drive_btn": tr("input_mouse_drive", default="Left Click"),
            "steer_btn": tr("input_mouse_steer", default="the Mouse Cursor"),
            "brake_btn": tr("input_kb_brake", default="\"X\""),
            "pause_btn": tr("input_kb_pause", default="ESC"),
            "radio_vol": tr("input_kb_radio_vol", default="W/S"),
            "radio_station": tr("input_kb_radio_station", default="A/D"),
            "drift_btn": tr("input_kb_drift", default="SHIFT")
        }

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

    def get_binding_texts(self) -> dict:
        from src.i18n import tr
        return {
            "drive_btn": tr("input_key_drive", default="the Arrow Keys"),
            "steer_btn": tr("input_key_steer", default="the Arrow Keys"),
            "brake_btn": tr("input_kb_brake", default="\"X\""),
            "pause_btn": tr("input_kb_pause", default="ESC"),
            "radio_vol": tr("input_kb_radio_vol", default="W/S"),
            "radio_station": tr("input_kb_radio_station", default="A/D"),
            "drift_btn": tr("input_kb_drift", default="SHIFT")
        }

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

    def get_binding_texts(self) -> dict:
        from src.i18n import tr
        return {
            "drive_btn": tr("input_pad_drive", default="the Left Stick"),
            "steer_btn": tr("input_pad_steer", default="the Left Stick"),
            "brake_btn": tr("input_pad_brake", default="L2/LT"),
            "pause_btn": tr("input_pad_pause", default="START"),
            "radio_vol": tr("input_pad_radio_vol", default="D-PAD Up/Down"),
            "radio_station": tr("input_pad_radio_station", default="L1/R1 RB/LB"),
            "drift_btn": tr("input_pad_drift", default="R2/RT")
        }

