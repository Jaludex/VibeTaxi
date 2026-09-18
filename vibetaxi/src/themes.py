import pygame
import settings
from gale.ui.theme import Theme

# Base / Default Theme used globally across Gale UI
DEFAULT_THEME = Theme(
    font=settings.FONTS["minecraft"],
    background_color=pygame.Color(69, 40, 60),
    hover_color=pygame.Color(100, 60, 90),
    focus_color=pygame.Color(100, 60, 90),
    border_color=pygame.Color(255, 255, 255),
    border_width=1
)

BUTTON_THEME = Theme(
    font=settings.FONTS["minecraft"],
    background_color=pygame.Color(100, 60, 90),
    hover_color=pygame.Color(150, 90, 120),
    focus_color=pygame.Color(150, 90, 120),
    text_color=pygame.Color(255, 255, 255),
    border_color=pygame.Color(255, 255, 255),
    border_width=1
)

DISABLED_BUTTON_THEME = Theme(
    font=settings.FONTS["minecraft"],
    background_color=pygame.Color(60, 40, 50),
    hover_color=pygame.Color(60, 40, 50),
    focus_color=pygame.Color(60, 40, 50),
    text_color=pygame.Color(150, 150, 150),
    border_color=pygame.Color(150, 150, 150),
    border_width=1
)

PANEL_THEME = Theme(
    background_color=pygame.Color(69, 40, 60),
    border_color=pygame.Color(255, 255, 255),
    border_width=2
)

LABEL_THEME = Theme(
    font=settings.FONTS["minecraft"],
    text_color=pygame.Color(255, 255, 255)
)

LABEL_GOLD_THEME = Theme(
    font=settings.FONTS["minecraft"],
    text_color=pygame.Color(255, 255, 50)
)

LABEL_GREEN_THEME = Theme(
    font=settings.FONTS["minecraft"],
    text_color=pygame.Color(100, 255, 100)
)

# Text Input
INPUT_THEME = Theme(
    font=settings.FONTS["minecraft"],
    background_color=pygame.Color(40, 20, 30),
    focus_color=pygame.Color(255, 200, 50),
    text_color=pygame.Color(255, 255, 255),
    border_color=pygame.Color(150, 150, 150),
    border_width=2,
    padding=5
)

# Text Box
TEXTBOX_THEME = Theme(
    font=settings.FONTS["minecraft"],
    background_color=pygame.Color(69, 40, 60),
    text_color=pygame.Color(255, 255, 255),
    border_width=0,
    padding=0
)

