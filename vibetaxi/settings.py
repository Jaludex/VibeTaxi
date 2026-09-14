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

TILED_UPPER_LAYERS = ["overheads"]
TILED_MIDDLE_LAYERS = ["decoration", "buildings"]
TILED_GROUND_LAYERS = ["ground"]

PASSENGER_DETECTION_RADIUS = 30
PASSENGER_DELIVERY_RADIUS = 60

TEXTURES = {
    "city_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "city_tileset.png"),
    "cars": pygame.image.load(BASE_DIR / "assets" / "graphics" / "cars.png"),
    "props": pygame.image.load(BASE_DIR / "assets" / "graphics" / "props.png"),
    "peds": pygame.image.load(BASE_DIR / "assets" / "graphics" / "peds.png")
}

# TILESET = tilemap.Tileset(TEXTURES["tiles"], TILE_SIZE, TILE_SIZE)

TILEMAPS = {
    "city": str(BASE_DIR / "assets" / "tilemaps" / "city.json")
}

FRAMES = {
    "cars": generate_car_frames(),
    "props": frames.generate_frames(TEXTURES["props"], 16, 16),
    "peds": frames.generate_frames(TEXTURES["peds"], 16, 16)
}

FONTS = {
    "big": pygame.font.Font(BASE_DIR / "assets" / "fonts" / "Big.ttf", 32),
}

SOUNDS = {

}

MUSIC_CHANNELS = {

}


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
