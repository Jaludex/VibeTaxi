"""
Persistent configuration manager for VibeTaxi.
Manages game settings (audio volumes, fullscreen, deadzone, fps, debug, language).
"""

from typing import Any, Dict
import settings

DEFAULTS: Dict[str, Any] = {
    "language": "es",
    "master_volume": 1.0,
    "music_volume": 0.8,
    "sfx_volume": 1.0,
    "engine_volume": 1.0,
    "ambient_volume": 1.0,
    "fullscreen": False,
    "gamepad_deadzone": 0.25,
    "show_fps": False,
    "physics_debug": False,
    "pause_on_focus_loss": True,
    "discord_rpc": True,
}

_config: Dict[str, Any] = {}
_loaded: bool = False


def load() -> Dict[str, Any]:
    global _config, _loaded
    if settings.SAVE_MANAGER.exists("config"):
        try:
            saved = settings.SAVE_MANAGER.load("config")
            if isinstance(saved, dict):
                _config = {**DEFAULTS, **saved}
            else:
                _config = dict(DEFAULTS)
        except Exception:
            _config = dict(DEFAULTS)
    else:
        _config = dict(DEFAULTS)

    _loaded = True
    _apply_to_settings()
    return _config


def _apply_to_settings() -> None:
    """Synchronize configuration values with global settings attributes."""
    if _config.get("language") is not None:
        settings.LANGUAGE = _config["language"]
    settings.GAMEPAD_DEADZONE = float(_config.get("gamepad_deadzone", 0.25))
    settings.SHOW_FPS = bool(_config.get("show_fps", False))
    settings.PHYSICS_DEBUG = bool(_config.get("physics_debug", False))


def get(key: str, default: Any = None) -> Any:
    global _loaded
    if not _loaded:
        load()
    if default is None:
        default = DEFAULTS.get(key)
    return _config.get(key, default)


def set(key: str, value: Any, auto_save: bool = False) -> None:
    global _loaded
    if not _loaded:
        load()
    _config[key] = value
    _apply_to_settings()
    if auto_save:
        save()


def save() -> None:
    global _loaded
    if not _loaded:
        load()
    try:
        settings.SAVE_MANAGER.save("config", _config)
    except Exception as e:
        print(f"Error saving config: {e}")


def reset_defaults() -> None:
    global _config
    # Keep current language when resetting other defaults
    current_lang = _config.get("language", DEFAULTS["language"])
    _config = dict(DEFAULTS)
    _config["language"] = current_lang
    _apply_to_settings()
    save()
