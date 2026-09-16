import pathlib
import settings

RADIO_STATIONS = [
    {
        "name": "off",
        "songs": []
    },
    {
        "name": "rock",
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "bombinsound-rock-music.mp3"),
            str(settings.BASE_DIR / "assets" / "music" / "jonasblakewood-rock.mp3"),
        ]
    },
    {
        "name": "pop",
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "happinessinmusic-pop-music.mp3"),
        ]
    },
    {
        "name": "hiphop",
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "kontraa-nba--hiphop-music.mp3"),
        ]
    },
    {
        "name": "electronic",
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "mondamusic-electronic-music.mp3"),
        ]
    }
]
