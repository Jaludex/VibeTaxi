from typing import Optional
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
            "drift_btn": tr("input_kb_drift", default="SHIFT"),
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
        max_dist = getattr(settings, "MOUSE_MAX_SPEED_RADIUS", 80)
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
            "drift_btn": tr("input_kb_drift", default="SHIFT"),
        }


class GamepadInputStrategy:
    def get_target_position(self, entity, dt):
        dx = getattr(entity, "steer_x", 0.0)
        dy = getattr(entity, "steer_y", 0.0)

        # Deadzone to prevent stick drift
        deadzone = getattr(settings, "GAMEPAD_DEADZONE", 0.25)
        if abs(dx) < deadzone: dx = 0
        if abs(dy) < deadzone: dy = 0

        if dx == 0 and dy == 0:
            entity.is_accelerating = False
            return entity.x, entity.y

        entity.is_accelerating = True
        dist_ratio = math.hypot(dx, dy)
        if dist_ratio > 1.0: dist_ratio = 1.0

        angle = math.atan2(dy, dx)
        max_dist = getattr(settings, "MOUSE_MAX_SPEED_RADIUS", 80)
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
            "drift_btn": tr("input_pad_drift", default="R2/RT"),
        }


class TouchDirectInputStrategy:
    """Steers the taxi towards the touch point on screen or using virtual joystick depending on configuration."""
    def get_target_position(self, entity, dt):
        mode = getattr(settings, "TOUCH_CONTROL_MODE", "touch")
        if mode == "joystick":
            dx = getattr(entity, "touch_joystick_x", 0.0)
            dy = getattr(entity, "touch_joystick_y", 0.0)

            deadzone = 0.12
            dist = math.hypot(dx, dy)
            if dist < deadzone:
                entity.is_accelerating = False
                return entity.x, entity.y

            entity.is_accelerating = True
            dist_ratio = min(1.0, dist)
            angle = math.atan2(dy, dx)
            max_dist = getattr(settings, "MOUSE_MAX_SPEED_RADIUS", 80)
            return entity.x + math.cos(angle) * max_dist * dist_ratio, entity.y + math.sin(angle) * max_dist * dist_ratio

        touch_active = getattr(entity, "touch_active", False)
        touch_x = getattr(entity, "touch_x", None)
        touch_y = getattr(entity, "touch_y", None)

        from src.os_tools import is_android
        if not is_android() and (not touch_active or touch_x is None or touch_y is None):
            # Fallback for mouse click/drag on desktop ONLY
            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
                px, py = pygame.mouse.get_pos()
                touch_x, touch_y = physical_to_virtual(px, py)
                touch_active = True

        if not touch_active or touch_x is None or touch_y is None:
            entity.is_accelerating = False
            return entity.x, entity.y

        entity.is_accelerating = True
        camera = getattr(entity, "camera", None)
        if camera:
            return camera.screen_to_world((touch_x, touch_y))
        return touch_x, touch_y

    def get_binding_texts(self) -> dict:
        mode = getattr(settings, "TOUCH_CONTROL_MODE", "touch")
        if mode == "joystick":
            return TouchJoystickInputStrategy().get_binding_texts()
        from src.i18n import tr
        return {
            "drive_btn": tr("input_touch_drive", default="Touching the Screen"),
            "steer_btn": tr("input_touch_steer", default="Your Finger"),
            "brake_btn": tr("input_touch_brake", default="the Brake Button"),
            "pause_btn": tr("input_touch_pause", default="the Pause Button"),
            "radio_vol": tr("input_touch_radio_vol", default="Radio Buttons"),
            "radio_station": tr("input_touch_radio_station", default="Radio Buttons"),
            "drift_btn": tr("input_touch_drift", default="the Drift Button"),
        }


class TouchJoystickInputStrategy:
    """Steers the taxi using an on-screen analog virtual joystick."""
    def get_target_position(self, entity, dt):
        mode = getattr(settings, "TOUCH_CONTROL_MODE", "touch")
        if mode != "joystick":
            return TouchDirectInputStrategy().get_target_position(entity, dt)

        dx = getattr(entity, "touch_joystick_x", 0.0)
        dy = getattr(entity, "touch_joystick_y", 0.0)

        deadzone = 0.12
        dist = math.hypot(dx, dy)
        if dist < deadzone:
            entity.is_accelerating = False
            return entity.x, entity.y

        entity.is_accelerating = True
        dist_ratio = min(1.0, dist)
        angle = math.atan2(dy, dx)
        max_dist = getattr(settings, "MOUSE_MAX_SPEED_RADIUS", 80)
        return entity.x + math.cos(angle) * max_dist * dist_ratio, entity.y + math.sin(angle) * max_dist * dist_ratio

    def get_binding_texts(self) -> dict:
        from src.i18n import tr
        return {
            "drive_btn": tr("input_joy_drive", default="the Virtual Joystick"),
            "steer_btn": tr("input_joy_steer", default="the Virtual Joystick"),
            "brake_btn": tr("input_touch_brake", default="the Brake Button"),
            "pause_btn": tr("input_touch_pause", default="the Pause Button"),
            "radio_vol": tr("input_touch_radio_vol", default="Radio Buttons"),
            "radio_station": tr("input_touch_radio_station", default="Radio Buttons"),
            "drift_btn": tr("input_touch_drift", default="the Drift Button"),
        }


def get_touch_strategy(mode: Optional[str] = None):
    """Return the configured touch strategy (direct or joystick)."""
    if mode is None:
        mode = getattr(settings, "TOUCH_CONTROL_MODE", "touch")
    if mode == "joystick":
        return TouchJoystickInputStrategy()
    return TouchDirectInputStrategy()
