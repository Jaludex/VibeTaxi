import pathlib

import pygame
import os

from gale import frames
from gale import input_handler
from gale import tilemap

from gale.save import SaveManager
from src.frame_tools import generate_car_frames

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_F11, "toggle_fullscreen")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "pause")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "mouse_click")
input_handler.InputHandler.set_mouse_motion_action(None, "mouse_motion")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_x, "brake")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_z, "reverse")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LSHIFT, "drift")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "prev-song")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "next-song")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_w, "vol-up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_s, "vol-down")

import string
# Map all printable keys for TextInput, without overwriting existing game controls
existing_keys = {
    input_handler.KEY_a, input_handler.KEY_d, input_handler.KEY_w, input_handler.KEY_s,
    input_handler.KEY_x, input_handler.KEY_z, input_handler.KEY_LSHIFT,
    input_handler.KEY_ESCAPE
}

for char in string.ascii_lowercase + string.digits:
    key_const = getattr(pygame, f"K_{char}", None)
    if key_const is not None and key_const not in existing_keys:
        input_handler.InputHandler.set_keyboard_action(key_const, "keyboard")

# Special keys for TextInput
for key_name in ["SPACE", "BACKSPACE", "RETURN", "KP_ENTER", "DELETE", "LEFT", "RIGHT"]:
    key_const = getattr(pygame, f"K_{key_name}", None)
    if key_const is not None and key_const not in existing_keys:
        input_handler.InputHandler.set_keyboard_action(key_const, "keyboard")



RADIO_FADEOUT_TIME = 2.0

TITLE = "Vibe Taxi"

VERSION = "1.0.0-beta2"

CREDITS = (
    "VIBE TAXI\n"
    "A game made with Gale Engine & Pygame.\nAs Project in the course of\nVideogame Programming I (ULA)\n"
    "Development & Design:\n"
    "Jesus Leon (Jaludex)\nZadkiel Jimenez (Eltoti)\n\n"
    "Music & Sound Effects:\n"
    "opengameart.org\npixabay.com\nText blips by dmochas on itch.io\n"
    "Graphical Assets:\n"
    "Radio, indicator arrow and passenger UI by Eltoti\n"
    "City Assets by nyknck on itch.io\n"
    "Cars textures by Kia on itch.io\n"
    "Peds texture by vimlark on itch.io\n"
    "Fonts:\nGoogle Fonts\n\n"
    "Thanks for playing our game!\nHope you enjoy it and have a good time!\n"
)



DIALOGUE_DISPLAY_TIME = 5.0

BASE_DIR = pathlib.Path(__file__).parent

SAVE_DIR = BASE_DIR / "saves"

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

CANT_MUSIC_CHANNELS = 5

PHYSICS_DEBUG = False

TEXTURES = {
    "city_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "city_tileset.png"),
    "cars": pygame.image.load(BASE_DIR / "assets" / "graphics" / "cars.png"),
    "props": pygame.image.load(BASE_DIR / "assets" / "graphics" / "props.png"),
    "radio": pygame.image.load(BASE_DIR / "assets" / "graphics" / "radio.png"),
    "button-radio": pygame.image.load(BASE_DIR / "assets" / "graphics" / "button_radio.png"),
    "button-plus": pygame.image.load(BASE_DIR / "assets" / "graphics" / "button_plus.png"),
    "button-less": pygame.image.load(BASE_DIR / "assets" / "graphics" / "button_less.png"),
    "marker": pygame.image.load(BASE_DIR / "assets" / "graphics" / "marker.png"),
    "peds": pygame.image.load(BASE_DIR / "assets" / "graphics" / "peds.png"),
    "arrow": pygame.image.load(BASE_DIR / "assets" / "graphics" / "arrow.png"),
    "title_gradient": pygame.image.load(BASE_DIR / "assets" / "graphics" / "title_gradient.png"),
    "taximeter": pygame.image.load(BASE_DIR / "assets" / "graphics" / "taximeter.png"),
    "background_car_view": pygame.image.load(BASE_DIR / "assets" / "graphics" / "background_car_view.png"),
    "game_icon": pygame.image.load(BASE_DIR / "assets" / "graphics" / "icon.png"),
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
    "peds": frames.generate_frames(TEXTURES["peds"], 16, 16)
}

FONTS = {
    "big": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Big.ttf", 32),
    "medium": pygame.font.Font(BASE_DIR/ "assets" / "fonts" / "Minecraft.ttf", 12),
    "led": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "led.ttf", 16),
    "led_small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "led.ttf", 8),
    "minecraft": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minecraft.ttf", 12),
    "minecraft_small": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Minecraft.ttf", 8),
}

SOUNDS = {
    "crash_car": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_car.wav"),
    "crash_mail": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_mail.wav"),
    "crash_solid": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_solid.wav"),
    "crash_wall": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "crash_sounds" / "crash_wall.wav"),
    "engine_start": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "engine_start.wav"),
    "drifting": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "drifting.wav"),
    "idle_normal": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "idle-normal.wav"),
    "idle_damaged": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "idle-damaged.wav"),
    "engine1": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "engine1.wav"),
    "engine2": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "engine2.wav"),
    "into_vibe": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "into_vibe.wav"),
    "out_vibe": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "out_vibe.wav"),
    "win": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "victory.wav"),
    "honk": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "car_sounds" / "car_honk.wav"),
    "money": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "gain_money.wav"),
    "fix": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "fix.wav"),
    "press": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "press.wav"),
    "game_over": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "game_over.wav"),
    "pause": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "pause.wav"),
    "unpause": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "misc" / "unpause.wav"),
    "bleep1": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep001.wav"),
    "bleep2": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep002.wav"),
    "bleep3": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep003.wav"),
    "bleep4": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep004.wav"),
    "bleep5": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "text_blips" / "bleep005.wav"),
}

MUSIC = {
    "menu": str(BASE_DIR / "assets" / "music" / "menu.ogg"),
}
REPAIR_COST = 40.0

SAVE_MANAGER = SaveManager(save_dir=BASE_DIR / 'saves')
