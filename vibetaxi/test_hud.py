import pygame
pygame.init()
pygame.display.set_mode((640, 360))
import settings
from src.gui.PassengerHUD import PassengerHUD
class MockPassenger:
    def __init__(self):
        self.comfort = 50
        self.dialogues = {}
        self.definition = {"texture": "peds"}
        self.frame_index = 0
hud = PassengerHUD()
surface = pygame.Surface((640, 360))
hud.passenger = MockPassenger()
hud.passenger_state = "riding"
hud.render_portrait(surface)
print("No crash on render!")
