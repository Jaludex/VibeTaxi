"""
Display and fullscreen management for VibeTaxi.
"""

import pygame
from src import config


def is_fullscreen() -> bool:
    surface = pygame.display.get_surface()
    if surface:
        return bool(surface.get_flags() & pygame.FULLSCREEN)
    return False


def set_fullscreen(enable: bool) -> None:
    current = is_fullscreen()
    if enable != current:
        try:
            pygame.display.toggle_fullscreen()
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")
    config.set("fullscreen", enable, auto_save=True)


def toggle_fullscreen() -> None:
    set_fullscreen(not is_fullscreen())


def init_display() -> None:
    """Apply saved fullscreen preference on game boot."""
    target_fs = config.get("fullscreen", False)
    if target_fs and not is_fullscreen():
        try:
            pygame.display.toggle_fullscreen()
        except Exception as e:
            print(f"Error initializing fullscreen: {e}")
