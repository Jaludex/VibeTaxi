"""
Central audio manager for VibeTaxi.
Handles volume scaling (Master, Music, SFX, Engine, Ambience) and playback.
"""

from typing import Optional, Union
import pygame
import settings
from src import config

_current_base_music_volume: float = 0.5


def master() -> float:
    return max(0.0, min(1.0, float(config.get("master_volume", 1.0))))


def music_scale() -> float:
    return master() * max(0.0, min(1.0, float(config.get("music_volume", 0.8))))


def sfx_scale() -> float:
    return master() * max(0.0, min(1.0, float(config.get("sfx_volume", 1.0))))


def engine_scale() -> float:
    return master() * max(0.0, min(1.0, float(config.get("engine_volume", 1.0))))


def ambient_scale() -> float:
    return master() * max(0.0, min(1.0, float(config.get("ambient_volume", 1.0))))


def set_music_volume(base_volume: Optional[float] = None) -> None:
    """Set the active background music volume, scaled by master and music volumes."""
    global _current_base_music_volume
    if base_volume is not None:
        _current_base_music_volume = max(0.0, min(1.0, base_volume))
    effective_vol = _current_base_music_volume * music_scale()
    try:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, effective_vol)))
    except Exception:
        pass


def refresh_music() -> None:
    """Re-apply the current music volume calculation."""
    set_music_volume()


def play_sfx(
    sound_or_key: Union[str, pygame.mixer.Sound],
    volume: float = 1.0,
    loops: int = 0
) -> Optional[pygame.mixer.Channel]:
    """Play a sound effect with category scaling applied to the allocated channel."""
    if isinstance(sound_or_key, str):
        sound = settings.SOUNDS.get(sound_or_key)
    else:
        sound = sound_or_key

    if not sound:
        return None

    effective_vol = max(0.0, min(1.0, volume * sfx_scale()))
    if effective_vol <= 0.001:
        return None

    try:
        channel = sound.play(loops=loops)
        if channel:
            channel.set_volume(effective_vol)
        return channel
    except Exception as e:
        print(f"Error playing sfx: {e}")
        return None


def play_preview(category: str = "sfx") -> None:
    """Play a brief audio feedback cue reflecting the volume of the modified category."""
    try:
        if category in ("sfx", "master"):
            vol = master() if category == "master" else sfx_scale()
            sound = settings.SOUNDS.get("bleep1") or settings.SOUNDS.get("press")
            if sound and vol > 0.01:
                ch = sound.play()
                if ch:
                    ch.set_volume(vol)
        elif category == "music":
            refresh_music()
            # Also play a soft blip if music is off/not playing
            if not pygame.mixer.music.get_busy() and music_scale() > 0.01:
                sound = settings.SOUNDS.get("bleep3")
                if sound:
                    ch = sound.play()
                    if ch:
                        ch.set_volume(music_scale())
        elif category == "engine":
            sound = settings.SOUNDS.get("bleep2")
            vol = engine_scale()
            if sound and vol > 0.01:
                ch = sound.play(maxtime=300)
                if ch:
                    ch.set_volume(vol)
        elif category == "ambient":
            sound = settings.SOUNDS.get("bleep4") or settings.SOUNDS.get("bleep1")
            vol = ambient_scale()
            if sound and vol > 0.01:
                ch = sound.play()
                if ch:
                    ch.set_volume(vol)
    except Exception:
        pass
