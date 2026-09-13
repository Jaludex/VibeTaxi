import pygame

from typing import List

def generate_car_frames() -> List[pygame.Rect]:
    frames = []

    frames.append(pygame.Rect(16, 0, 14, 28))

    return frames