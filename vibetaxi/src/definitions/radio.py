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
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "bombinsound-rock-music.mp3"),
            str(settings.BASE_DIR / "assets" / "music" / "jonasblakewood-rock.mp3"),
        ]
    },
    {
        "name": "93.8FM Non-Stop-Pop",
        "genre": "pop",
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "happinessinmusic-pop-music.mp3"),
        ]
    },
    {
        "name": "101.2FM Hip-Hop Tunes",
        "genre": "hiphop",
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "kontraa-nba--hiphop-music.mp3"),
        ]
    },
    {
        "name": "107.9FM Electronic Dreamzzz",
        "genre": "electronic",
        "songs": [
            str(settings.BASE_DIR / "assets" / "music" / "mondamusic-electronic-music.mp3"),
        ]
    }
]
