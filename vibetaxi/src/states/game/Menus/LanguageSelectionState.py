import pygame
import settings
from gale.state import BaseState
from gale.timer import Timer
from gale.ui.manager import UIManager
from gale.ui.button import Button
from gale.ui.container import Container
from gale.text import render_text

from src.themes import BUTTON_THEME
from src.i18n import texts, tr

class LanguageSelectionState(BaseState):
    def __init__(self, state_machine, on_close=None):
        super().__init__(state_machine)
        self.on_close = on_close
        
    def enter(self, enter_params=None):
        self.container_y = settings.VIRTUAL_HEIGHT + 200
        self.target_y = settings.VIRTUAL_HEIGHT / 2
        
        container = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        
        available_langs = list(texts.keys())
        
        # Calculate buttons layout
        button_width = 150
        button_height = 30
        spacing = 10
        total_height = len(available_langs) * button_height + (len(available_langs) - 1) * spacing
        start_y = (settings.VIRTUAL_HEIGHT - total_height) / 2 + 20
        
        self.buttons = []
        for i, lang_code in enumerate(available_langs):
            # Display language code natively if possible, or use the tr functionality 
            # Or just show the language code for simplicity (e.g., 'en', 'es')
            # Let's display the name in its own language or upper case
            display_name = texts[lang_code].get("language_name", lang_code.upper())
            
            btn = Button(
                settings.VIRTUAL_WIDTH / 2 - button_width / 2, 
                start_y + i * (button_height + spacing),
                button_width, button_height,
                display_name,
                on_click=lambda l=lang_code: self._on_language_select(l),
                theme=BUTTON_THEME
            )
            container.add_child(btn)
            self.buttons.append(btn)
            
        self.ui = UIManager(
            container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )
        
        # Update Y position of all buttons to follow container_y
        self._update_ui_y()
        
        Timer.tween(0.4, [(self, {"container_y": self.target_y})], ease_function_name="out_cubic")
        
    def _update_ui_y(self):
        offset_y = self.container_y - self.target_y
        start_y = (settings.VIRTUAL_HEIGHT - (len(self.buttons) * 30 + (len(self.buttons) - 1) * 10)) / 2 + 20
        for i, btn in enumerate(self.buttons):
            btn.y = start_y + i * 40 + offset_y
            
    def update(self, dt):
        self._update_ui_y()
        self.ui.update(dt)
        
    def on_input(self, input_id, input_data):
        self.ui.on_input(input_id, input_data)
        
    def render(self, surface):
        if len(self.state_machine.states) <= 1:
            surface.fill((20, 20, 30))
            gradient = settings.TEXTURES.get("title_gradient")
            if gradient:
                surface.blit(gradient, (0, 0))
                
        # Draw a dim background
        dim = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        surface.blit(dim, (0, 0))
        
        # Draw the title
        title_y = self.container_y - 100
        render_text(
            surface,
            tr("msg_lang_title"),
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            title_y,
            (255, 255, 255),
            center=True,
            shadowed=True
        )
        
        self.ui.render(surface)
        
    def _on_language_select(self, lang_code):
        settings.SOUNDS["press"].play()
        settings.LANGUAGE = lang_code
        
        # Save configuration
        config = {}
        if settings.SAVE_MANAGER.exists("config"):
            config = settings.SAVE_MANAGER.load("config")
        config["language"] = lang_code
        settings.SAVE_MANAGER.save("config", config)
        
        Timer.tween(
            0.3, 
            [(self, {"container_y": settings.VIRTUAL_HEIGHT + 200})], 
            ease_function_name="in_cubic",
            on_finish=self._close
        )
        
    def _close(self):
        self.state_machine.pop()
        if self.on_close:
            self.on_close()
