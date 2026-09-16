import pathlib

import pygame

from gale import frames
from gale import input_handler
from gale import tilemap

from src.frame_tools import generate_car_frames

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "mouse_click")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_x, "brake")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_z, "reverse")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LSHIFT, "drift")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "prev-song")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "next-song")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_w, "vol-up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_s, "vol-down")

#DEBUG
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_TAB, "toggle_vibe")

RADIO_FADEOUT_TIME = 2.0

TITLE = "Vibe Taxi"

SAVE_SLOTS = ["slot1", "slot2", "slot3"]

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

TRAFFIC_SPAWN_INTERVAL = 0.2
TRAFFIC_MAX_CARS = 20

TEXTURES = {
    "city_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "city_tileset.png"),
    "cars": pygame.image.load(BASE_DIR / "assets" / "graphics" / "cars.png"),
    "props": pygame.image.load(BASE_DIR / "assets" / "graphics" / "props.png"),
    "radio": pygame.image.load(BASE_DIR / "assets" / "graphics" / "radio.png"),
    "button-radio": pygame.image.load(BASE_DIR / "assets" / "graphics" / "button_radio.png"),
    "button-plus": pygame.image.load(BASE_DIR / "assets" / "graphics" / "button_plus.png"),
    "button-less": pygame.image.load(BASE_DIR / "assets" / "graphics" / "button_less.png"),
    "marker": pygame.image.load(BASE_DIR / "assets" / "graphics" / "marker.png"),
    "peds": pygame.image.load(BASE_DIR / "assets" / "graphics" / "peds.png")
}

# TILESET = tilemap.Tileset(TEXTURES["tiles"], TILE_SIZE, TILE_SIZE)

TILEMAPS = {
    "city": str(BASE_DIR / "assets" / "tilemaps" / "city.json")
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
    "minecraft": pygame.font.Font(BASE_DIR/ "assets" / "fonts" / "Minecraft.ttf", 8)
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
}

CANT_MUSIC_CHANNELS = 5


PHYSICS_DEBUG = True


def play_music(name: str) -> None:
    stop_music(name)
    MUSIC_CHANNELS[name] = SOUNDS[name].play(loops=-1)


def stop_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.stop()
        MUSIC_CHANNELS[name] = None


def pause_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.pause()


def resume_music(name: str) -> None:
    channel = MUSIC_CHANNELS.get(name)

    if channel is not None:
        channel.unpause()
