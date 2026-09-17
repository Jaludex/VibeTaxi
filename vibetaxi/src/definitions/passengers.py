from typing import Any, Dict
import random 

PASSENGER_DEFS: Dict[str, Dict[str, Any]] = {
    "pedestrian_1": {
        "texture": "peds",
        "animations": {
            "idle": {"frames": [0, 1], "interval": 0.4},
            "walk": {"frames": [2, 3, 4, 5], "interval": 0.15},
        },
        "music_preference": "",
        "dialogues": "",
    },
    "pedestrian_2": {
        "texture": "peds",
        "animations": {
            "idle": {"frames": [6, 7], "interval": 0.4},
            "walk": {"frames": [8, 9, 10, 11], "interval": 0.15},
        },
        "music_preference": "",
        "dialogues": "",
    },
    "pedestrian_3": {
        "texture": "peds",
        "animations": {
            "idle": {"frames": [12, 13], "interval": 0.4},
            "walk": {"frames": [14, 15, 16, 17], "interval": 0.15},
        },
        "music_preference": "",
        "dialogues": "",
    },
    "pedestrian_4": {
        "texture": "peds",
        "animations": {
            "idle": {"frames": [18, 19], "interval": 0.4},
            "walk": {"frames": [20, 21, 22, 23], "interval": 0.15},
        },
        "music_preference": "",
        "dialogues": "",
    },
    "pedestrian_5": {
        "texture": "peds",
        "animations": {
            "idle": {"frames": [24, 25], "interval": 0.4},
            "walk": {"frames": [26, 27, 28, 29], "interval": 0.15},
        },
        "music_preference": "",
        "dialogues": "",
    },
}