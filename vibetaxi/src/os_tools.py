import os
import platform
import subprocess

from src.definitions.radio import USERTRACKS_DIR
from pathlib import Path

def open_user_tracks_folder(folder_path: Path = USERTRACKS_DIR):
    folder_path.mkdir(parents=True, exist_ok=True)

    system_name = platform.system()

    if system_name == "Windows":
        os.startfile(folder_path)
    elif system_name == "Darwin":
        subprocess.run(["open", str(folder_path)])
    else:
        subprocess.run(["xdg-open", str(folder_path)])