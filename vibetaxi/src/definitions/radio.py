import pathlib
import settings

RADIO_STATIONS = [
    {
        "name": "off",
        "songs": []
    },
    {
        "name": "87.5FM Rock For Life",
        "genre": "rock",
        "songs": [str(settings.BASE_DIR / "assets" / "music" / f"rock_{i}.mp3") for i in range(1, 6)]
    },
    {
        "name": "93.8FM Non-Stop-Pop",
        "genre": "pop",
        "songs": [str(settings.BASE_DIR / "assets" / "music" / f"pop_{i}.mp3") for i in range(1, 6)]
    },
    {
        "name": "98.2FM Smooth Jazz",
        "genre": "jazz",
        "songs": [str(settings.BASE_DIR / "assets" / "music" / f"jazz_{i}.mp3") for i in range(1, 5)]
    },
    {
        "name": "101.2FM Hip-Hop Tunes",
        "genre": "hiphop",
        "songs": [str(settings.BASE_DIR / "assets" / "music" / f"hiphop_{i}.mp3") for i in range(1, 4)]
    },
    {
        "name": "107.9FM Electronic Dreamzzz",
        "genre": "electronic",
        "songs": [str(settings.BASE_DIR / "assets" / "music" / f"electronic_{i}.mp3") for i in range(1, 6)]
    }
]
