import pathlib

import pygame

from gale import frames
from gale import input_handler
from gale import tilemap

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "mouse_click")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_x, "brake")


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

TEXTURES = {
    
}

# TILESET = tilemap.Tileset(TEXTURES["tiles"], TILE_SIZE, TILE_SIZE)

FRAMES = {
    
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
