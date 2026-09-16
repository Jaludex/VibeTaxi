import pygame

from typing import List

def generate_car_frames() -> List[pygame.Rect]:
    frames = []

    frames.append(pygame.Rect(0, 0, 14, 28))
    frames.append(pygame.Rect(16, 0, 14, 25))
    frames.append(pygame.Rect(32, 0, 16, 29))
    frames.append(pygame.Rect(48, 0, 16, 30))
    frames.append(pygame.Rect(64, 0, 14, 25))
    frames.append(pygame.Rect(0, 32, 16, 30))
    frames.append(pygame.Rect(34, 32, 18, 30))
    frames.append(pygame.Rect(52, 32, 20, 35))

    return frames