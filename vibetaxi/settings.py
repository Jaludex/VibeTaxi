import pathlib

import pygame
import os

from gale import frames
from gale import input_handler
from gale import tilemap

from gale.save import SaveManager
from src.frame_tools import generate_car_frames
from src.os_tools import get_save_dir

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_F11, "toggle_fullscreen")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "pause")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_AC_BACK, "pause")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "mouse_click")
input_handler.InputHandler.set_mouse_motion_action(None, "mouse_motion")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_x, "brake")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LSHIFT, "drift")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "prev-song")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "next-song")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_w, "vol-up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_s, "vol-down")

# Multi-touch SDL2 support for mobile
class FingerTouchData:
    def __init__(self, event: pygame.event.Event) -> None:
        self.pressed = event.type == pygame.FINGERDOWN
        self.released = event.type == pygame.FINGERUP
        self.motion = event.type == pygame.FINGERMOTION
        self.finger_id = getattr(event, "finger_id", 0)
        self.x = event.x
        self.y = event.y
        self.dx = getattr(event, "dx", 0.0)
        self.dy = getattr(event, "dy", 0.0)
        try:
            from src.mouse_tools import finger_to_virtual
            self.vx, self.vy = finger_to_virtual(event.x, event.y)
        except Exception:
            self.vx = event.x * VIRTUAL_WIDTH
            self.vy = event.y * VIRTUAL_HEIGHT

        if self.pressed or self.released:
            try:
                import gale.log
                gale.log.get_logger("touch").info(
                    f"FINGER {'DOWN' if self.pressed else 'UP'}: id={self.finger_id} raw=({self.x:.3f}, {self.y:.3f}) -> virt=({self.vx:.1f}, {self.vy:.1f})"
                )
            except Exception:
                pass

    @staticmethod
    def get_action_key(event: pygame.event.Event):
        return None

    @staticmethod
    def get_action_name():
        return "finger_touch"

input_handler.INPUT_EVENTS = input_handler.INPUT_EVENTS + (
    pygame.FINGERDOWN,
    pygame.FINGERUP,
    pygame.FINGERMOTION,
)
try:
    import gale.game
    gale.game.INPUT_EVENTS = input_handler.INPUT_EVENTS
except Exception:
    pass

input_handler.InputHandler.INPUT_DATA_TABLE[pygame.FINGERDOWN] = FingerTouchData
input_handler.InputHandler.INPUT_DATA_TABLE[pygame.FINGERUP] = FingerTouchData
input_handler.InputHandler.INPUT_DATA_TABLE[pygame.FINGERMOTION] = FingerTouchData
input_handler.InputHandler.input_binding["finger_touch"] = {None: "touch_event"}

# Gamepad bindings
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_LEFTSHOULDER, "prev-song")
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_RIGHTSHOULDER, "next-song")

# Navigation and Menu bindings (Keyboard)
input_handler.InputHandler.set_keyboard_action(pygame.K_UP, "move_up")
input_handler.InputHandler.set_keyboard_action(pygame.K_DOWN, "move_down")
input_handler.InputHandler.set_keyboard_action(pygame.K_LEFT, "move_left")
input_handler.InputHandler.set_keyboard_action(pygame.K_RIGHT, "move_right")
input_handler.InputHandler.set_keyboard_action(pygame.K_RETURN, "confirm")
input_handler.InputHandler.set_keyboard_action(pygame.K_SPACE, "confirm")

# Navigation bindings (Gamepad)
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_DPAD_UP, "vol-up")
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_DPAD_DOWN, "vol-down")
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_DPAD_LEFT, "move_left")
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_DPAD_RIGHT, "move_right")
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_A, "confirm")
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_X, "confirm")
input_handler.InputHandler.set_gamepad_button_action(input_handler.GAMEPAD_BUTTON_START, "pause")

# Analog driving bindings (Gamepad)
input_handler.InputHandler.set_gamepad_axis_action(input_handler.GAMEPAD_AXIS_LEFT_X, "steer_x")
input_handler.InputHandler.set_gamepad_axis_action(input_handler.GAMEPAD_AXIS_LEFT_Y, "steer_y")
input_handler.InputHandler.set_gamepad_axis_action(input_handler.GAMEPAD_AXIS_TRIGGER_LEFT, "trigger_brake")
input_handler.InputHandler.set_gamepad_axis_action(input_handler.GAMEPAD_AXIS_TRIGGER_RIGHT, "trigger_drift")

import string
# Map all printable keys for TextInput, without overwriting existing game controls
existing_keys = {
    input_handler.KEY_a, input_handler.KEY_d, input_handler.KEY_w, input_handler.KEY_s,
    input_handler.KEY_x, input_handler.KEY_LSHIFT,
    input_handler.KEY_ESCAPE, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_RETURN, pygame.K_SPACE
}

for char in string.ascii_lowercase + string.digits:
    key_const = getattr(pygame, f"K_{char}", None)
    if key_const is not None and key_const not in existing_keys:
        input_handler.InputHandler.set_keyboard_action(key_const, "keyboard")

# Special keys for TextInput
for key_name in ["BACKSPACE", "KP_ENTER", "DELETE"]:
    key_const = getattr(pygame, f"K_{key_name}", None)
    if key_const is not None and key_const not in existing_keys:
        input_handler.InputHandler.set_keyboard_action(key_const, "keyboard")



RADIO_FADEOUT_TIME = 2.0

TITLE = "Vibe Taxi"

VERSION = "1.5.0"


DIALOGUE_DISPLAY_TIME = 5.0
ALLOW_GAMEOVER_SKIP = False
TUTORIAL_ENABLED = False

BASE_DIR = pathlib.Path(__file__).parent

SAVE_DIR = get_save_dir(BASE_DIR / "saves")

VIRTUAL_WIDTH = 640
VIRTUAL_HEIGHT = 360

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

TILE_SIZE = 16

TILE_WIDTH = VIRTUAL_WIDTH // TILE_SIZE
TILE_HEIGHT = VIRTUAL_HEIGHT // TILE_SIZE

CAMERA_FOLLOW_RATE = 8.0

TILED_UPPER_SHADOW_LAYERS = ["overheads"]
TILED_UPPER_NO_SHADOW_LAYERS = ["decoration-high"]
TILED_MIDDLE_LAYERS = ["decoration-low", "buildings"]
TILED_GROUND_LAYERS = ["ground"]

PASSENGER_DETECTION_RADIUS = 30
PASSENGER_DELIVERY_RADIUS = 60

PASSENGER_NEXT_PAGE_TIME = 1.0
BAD_MUSIC_PENALTY_TIME = 1.5
MOUSE_MAX_SPEED_RADIUS = 80
GAMEPAD_DEADZONE = 0.25

# Vibe Mode Ghosting
GHOSTING_SPAWN_RATE = 0.08  # seconds between ghosts
GHOSTING_DURATION = 0.4     # seconds until alpha reaches 0
GHOSTING_ALPHA_START = 120  # initial alpha (0-255)

# Arcade Scoring
ARCADE_BASE_SCORE = 150
ARCADE_TIME_BONUS_SCORE = 50
ARCADE_SAFETY_BONUS_SCORE = 50

# Ranks
RANKS = [
    {"name": "F", "color": (150, 150, 150), "workday_min": 1, "arcade_min": 0, "sound": "fatal"},
    {"name": "E", "color": (200, 100, 100), "workday_min": 2, "arcade_min": 350, "sound": "bad"},
    {"name": "D", "color": (200, 150, 50),  "workday_min": 3, "arcade_min": 700, "sound": "bad"},
    {"name": "C", "color": (200, 200, 50),  "workday_min": 4, "arcade_min": 1050, "sound": "good"},
    {"name": "B", "color": (100, 200, 100), "workday_min": 5, "arcade_min": 1400, "sound": "good"},
    {"name": "A", "color": (50, 200, 255),  "workday_min": 6, "arcade_min": 1750, "sound": "awesome"},
    {"name": "VIBE", "color": (255, 50, 255), "workday_min": 8, "arcade_min": 2100, "sound": "vibe"},
]

COLOR_TRIP_SHORT = (0, 255, 0)
COLOR_TRIP_MEDIUM = (255, 255, 0)
COLOR_TRIP_LONG = (255, 69, 0)

COLOR_PASSENGER_DELIVERY = (0, 255, 0)

VIBE_COLORS = {
    "rock": (255, 50, 50),
    "pop": (255, 105, 180),
    "hiphop": (255, 200, 0),
    "electronic": (50, 255, 255),
    "jazz": (50, 100, 255),
    "off": (150, 255, 150)
}

TRAFFIC_SPAWN_INTERVAL = 0.2
TRAFFIC_MAX_CARS = 20

PEDESTRIAN_SPAWN_INTERVAL = 0.8
PEDESTRIAN_MAX_COUNT = 25
PEDESTRIAN_SPAWN_RANGE = 600
PEDESTRIAN_MAX_DISTANCE = 900
PEDESTRIAN_SPAWN_CHANCE = 0.65

CANT_MUSIC_CHANNELS = 5

PHYSICS_DEBUG = False

def _load_texture(path):
    try:
        if not pygame.display.get_init():
            pygame.display.init()
        return pygame.image.load(path)
    except Exception as e:
        print(f"Warning: Failed to load texture {path}: {e}")
        return pygame.Surface((16, 16))

def _load_font(path, size):
    try:
        if not pygame.font.get_init():
            pygame.font.init()
        return pygame.font.Font(path, size)
    except Exception as e:
        print(f"Warning: Failed to load font {path}: {e}")
        return pygame.font.Font(None, size)

class DummySound:
    def play(self, *args, **kwargs):
        pass
    def stop(self, *args, **kwargs):
        pass
    def set_volume(self, *args, **kwargs):
        pass
    def get_volume(self):
        return 1.0
    def get_length(self):
        return 0.0

def _load_sound(path):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 2048)
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Warning: Failed to load sound {path}: {e}")
        return DummySound()

TEXTURES = {
    "city_tiles": _load_texture(BASE_DIR / "assets" / "graphics" / "city_tileset.png"),
    "cars": _load_texture(BASE_DIR / "assets" / "graphics" / "cars.png"),
    "props": _load_texture(BASE_DIR / "assets" / "graphics" / "props.png"),
    "radio": _load_texture(BASE_DIR / "assets" / "graphics" / "radio.png"),
    "button-radio": _load_texture(BASE_DIR / "assets" / "graphics" / "button_radio.png"),
    "button-plus": _load_texture(BASE_DIR / "assets" / "graphics" / "button_plus.png"),
    "button-less": _load_texture(BASE_DIR / "assets" / "graphics" / "button_less.png"),
    "marker": _load_texture(BASE_DIR / "assets" / "graphics" / "marker.png"),
    "peds": _load_texture(BASE_DIR / "assets" / "graphics" / "peds.png"),
    "arrow": _load_texture(BASE_DIR / "assets" / "graphics" / "arrow.png"),
    "title_gradient": _load_texture(BASE_DIR / "assets" / "graphics" / "title_gradient.png"),
    "taximeter": _load_texture(BASE_DIR / "assets" / "graphics" / "taximeter.png"),
    "background_car_view": _load_texture(BASE_DIR / "assets" / "graphics" / "background_car_view.png"),
    "game_icon": _load_texture(BASE_DIR / "assets" / "graphics" / "icon.png"),
    "music_notes": _load_texture(BASE_DIR / "assets" / "graphics" / "music_notes.png"),
}

TILEMAPS = {
    "city": str(BASE_DIR / "assets" / "tilemaps" / "city.json"),
    "tutorial": str(BASE_DIR / "assets" / "tilemaps" / "tutorial.json")
}

FRAMES = {
    "cars": generate_car_frames(),
    "props": frames.generate_frames(TEXTURES["props"], 16, 16),
    "button-less": frames.generate_frames(TEXTURES["button-less"], 47, 24),
    "button-plus": frames.generate_frames(TEXTURES["button-plus"], 47, 24),
    "peds": frames.generate_frames(TEXTURES["peds"], 16, 16),
    "music_notes": frames.generate_frames(TEXTURES["music_notes"], 12, 15)
}

FONTS = {
    "rank": _load_font(BASE_DIR / "assets" / "fonts" / "Big.ttf", 64),
    "big": _load_font(BASE_DIR / "assets" / "fonts" / "Big.ttf", 32),
    "medium": _load_font(BASE_DIR/ "assets" / "fonts" / "medium.ttf", 14),
    "led": _load_font(BASE_DIR / "assets" / "fonts" / "led.ttf", 16),
    "led_small": _load_font(BASE_DIR / "assets" / "fonts" / "led.ttf", 8),
    "minecraft": _load_font(BASE_DIR / "assets" / "fonts" / "medium.ttf", 14),
    "minecraft_small": _load_font(BASE_DIR / "assets" / "fonts" / "medium.ttf", 11),
}

SOUNDS = {
    "crash_car": _load_sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_car.wav"),
    "crash_mail": _load_sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_mail.wav"),
    "crash_solid": _load_sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_solid.wav"),
    "crash_wall": _load_sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_wall.wav"),
    "engine_start": _load_sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "engine_start.wav"),
    "drifting": _load_sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "drifting.wav"),
    "idle_normal": _load_sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "idle-normal.wav"),
    "idle_damaged": _load_sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "idle-damaged.wav"),
    "engine1": _load_sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "engine1.wav"),
    "engine2": _load_sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "engine2.wav"),
    "into_vibe": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "into_vibe.wav"),
    "out_vibe": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "out_vibe.wav"),
    "win": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "victory.wav"),
    "honk": _load_sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "car_honk.wav"),
    "money": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "gain_money.wav"),
    "fix": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "fix.wav"),
    "press": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "press.wav"),
    "game_over": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "game_over.wav"),
    "pause": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "pause.wav"),
    "unpause": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "unpause.wav"),
    "bleep1": _load_sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep001.wav"),
    "bleep2": _load_sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep002.wav"),
    "bleep3": _load_sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep003.wav"),
    "bleep4": _load_sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep004.wav"),
    "bleep5": _load_sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep005.wav"),
    "bonus": _load_sound(BASE_DIR / "assets" / "sounds" / "misc" / "bonus.wav"),
    "fatal": _load_sound(BASE_DIR / "assets" / "sounds" / "ranks" / "fatal.ogg"),
    "bad": _load_sound(BASE_DIR / "assets" / "sounds" / "ranks" / "bad.wav"),
    "good": _load_sound(BASE_DIR / "assets" / "sounds" / "ranks" / "good.ogg"),
    "awesome": _load_sound(BASE_DIR / "assets" / "sounds" / "ranks" / "awesome.wav"),
    "vibe": _load_sound(BASE_DIR / "assets" / "sounds" / "ranks" / "vibe.wav"),
}

MUSIC = {
    "menu": str(BASE_DIR / "assets" / "music" / "menu.ogg"),
}
REPAIR_COST = 40.0

SAVE_MANAGER = SaveManager(save_dir=SAVE_DIR)

# Configurable runtime flags
SHOW_FPS = False
PHYSICS_DEBUG = False
LANGUAGE = None
TOUCH_CONTROL_MODE = "touch"
DISCORD_CLIENT_ID = "1558733170730344582"

try:
    from src import config
    config.load()
except Exception:
    if SAVE_MANAGER.exists("config"):
        _config = SAVE_MANAGER.load("config")
        LANGUAGE = _config.get("language")
