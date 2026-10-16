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


import ctypes
import glob
import os
from typing import Optional

_cached_refresh_rate: Optional[int] = None
_cached_sdl2_lib = None


def _get_sdl2_cdll():
    global _cached_sdl2_lib
    if _cached_sdl2_lib is not None:
        return _cached_sdl2_lib

    # 1. Check proc maps (Linux)
    if os.path.exists("/proc/self/maps"):
        try:
            with open("/proc/self/maps") as f:
                for line in f:
                    if "libSDL2-" in line and ".so" in line:
                        p = line.split()[-1]
                        try:
                            c = ctypes.CDLL(p)
                            if hasattr(c, "SDL_GetCurrentDisplayMode"):
                                _cached_sdl2_lib = c
                                return c
                        except Exception:
                            pass
        except Exception:
            pass

    # 2. Check pygame package directory / pygame.libs (Windows, Linux, Mac wheels)
    pyg_dir = os.path.dirname(pygame.__file__)
    candidates = (
        glob.glob(os.path.join(pyg_dir, "..", "pygame.libs", "*SDL2*"))
        + glob.glob(os.path.join(pyg_dir, "*SDL2*"))
        + glob.glob(os.path.join(pyg_dir, "*.dll"))
    )
    for p in candidates:
        try:
            c = ctypes.CDLL(p)
            if hasattr(c, "SDL_GetCurrentDisplayMode"):
                _cached_sdl2_lib = c
                return c
        except Exception:
            pass

    # 3. Standard ctypes library lookup
    for name in ["libSDL2-2.0.so.0", "SDL2.dll", "libSDL2.dylib", "SDL2"]:
        try:
            c = ctypes.CDLL(name)
            if hasattr(c, "SDL_GetCurrentDisplayMode"):
                _cached_sdl2_lib = c
                return c
        except Exception:
            pass

    return None


class _SDL_DisplayMode(ctypes.Structure):
    _fields_ = [
        ("format", ctypes.c_uint32),
        ("w", ctypes.c_int),
        ("h", ctypes.c_int),
        ("refresh_rate", ctypes.c_int),
        ("driverdata", ctypes.c_void_p),
    ]


def get_monitor_refresh_rate() -> int:
    """
    Detect the physical monitor's refresh rate (Hz) using SDL2.
    Falls back to 60 Hz if detection fails or in virtual/headless displays.
    """
    global _cached_refresh_rate
    if _cached_refresh_rate is not None and _cached_refresh_rate > 0:
        return _cached_refresh_rate

    try:
        sdl = _get_sdl2_cdll()
        if sdl:
            mode = _SDL_DisplayMode()
            if sdl.SDL_GetCurrentDisplayMode(0, ctypes.byref(mode)) == 0:
                if mode.refresh_rate > 0:
                    _cached_refresh_rate = int(mode.refresh_rate)
                    return _cached_refresh_rate
    except Exception:
        pass

    return 60
