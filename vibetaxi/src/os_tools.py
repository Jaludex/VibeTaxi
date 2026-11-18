import os
import platform
import subprocess
from pathlib import Path


def is_android() -> bool:
    """Return True if running on an Android device via python-for-android."""
    return (
        "ANDROID_ARGUMENT" in os.environ
        or "ANDROID_PRIVATE" in os.environ
        or os.environ.get("VIBETAXI_FORCE_ANDROID") == "1"
    )


def is_mobile_mode() -> bool:
    """Return True if running on Android or previewing mobile mode on desktop."""
    return is_android() or os.environ.get("VIBETAXI_MOBILE_PREVIEW") == "1"


def get_save_dir(default_dir: Path) -> Path:
    """Return persistent save directory for the platform."""
    if is_android() and "ANDROID_PRIVATE" in os.environ:
        path = Path(os.environ["ANDROID_PRIVATE"]) / "saves"
        path.mkdir(parents=True, exist_ok=True)
        return path
    return default_dir


def open_user_tracks_folder(folder_path: Path):
    if is_android():
        # Opening external file managers via subprocess is not supported on Android
        return

    folder_path.mkdir(parents=True, exist_ok=True)
    system_name = platform.system()

    if system_name == "Windows":
        os.startfile(folder_path)
    elif system_name == "Darwin":
        subprocess.run(["open", str(folder_path)])
    else:
        try:
            subprocess.run(["xdg-open", str(folder_path)])
        except Exception:
            pass
