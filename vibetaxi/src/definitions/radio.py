from pathlib import Path

import pygame
import settings

USERTRACKS_DIR = Path.home() / "Vibe Taxi User Tracks"
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".ogg", ".wav"}

def is_valid_audio(file_path: Path) -> bool:
    try:
        pygame.mixer.music.load(str(file_path))
        return True
    except pygame.error:
        return False

def get_station_tracks(genre: str, base_tracks: list) -> list:
    if genre == "off":
        return []

    genre_dir = USERTRACKS_DIR / genre
    
    genre_dir.mkdir(parents=True, exist_ok=True)

    user_tracks = []
    
    for file in genre_dir.iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
            if is_valid_audio(file):
                user_tracks.append(str(file))

    return base_tracks + user_tracks


RADIO_STATIONS = [
    {
        "name": "off",
        "genre": "off",
        "songs": get_station_tracks("off", [])
    },
    {
        "name": "87.5FM Rock For Life",
        "genre": "rock",
        "songs": get_station_tracks(
            "rock",
            [str(settings.BASE_DIR / "assets" / "music" / f"rock_{i}.mp3") for i in range(1, 6)]
        )
    },
    {
        "name": "93.8FM Non-Stop-Pop",
        "genre": "pop",
        "songs": get_station_tracks(
            "pop",
            [str(settings.BASE_DIR / "assets" / "music" / f"pop_{i}.mp3") for i in range(1, 6)]
        )
    },
    {
        "name": "98.2FM Smooth Jazz",
        "genre": "jazz",
        "songs": get_station_tracks(
            "jazz",
            [str(settings.BASE_DIR / "assets" / "music" / f"jazz_{i}.mp3") for i in range(1, 5)]
        )
    },
    {
        "name": "101.2FM Hip-Hop Tunes",
        "genre": "hiphop",
        "songs": get_station_tracks(
            "hiphop",
            [str(settings.BASE_DIR / "assets" / "music" / f"hiphop_{i}.mp3") for i in range(1, 4)]
        )
    },
    {
        "name": "107.9FM Electronic Dreamzzz",
        "genre": "electronic",
        "songs": get_station_tracks(
            "electronic",
            [str(settings.BASE_DIR / "assets" / "music" / f"electronic_{i}.mp3") for i in range(1, 6)]
        )
    }
]