import pygame
pygame.init()
import settings
pygame.display.set_mode((640, 360))
from src.gui.PassengerHUD import PassengerHUD
hud = PassengerHUD()
surface = pygame.Surface((640, 360))
hud.render_portrait(surface)
print("No crash on render!")
