from typing import Optional, Callable
import pygame
import random

from gale.ui.text_box import TextBox
from gale.ui.theme import Theme
from gale.text import Text
import settings

class TypewriterTextBox(TextBox):
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        text: str,
        font: Optional[pygame.font.Font] = None,
        lines_per_page: int = 3,
        on_close: Optional[Callable[[], None]] = None,
        theme: Optional[Theme] = None,
        chars_per_second: float = 40.0
    ) -> None:
        super().__init__(x, y, width, height, text, font, lines_per_page, on_close, theme)
        self.chars_per_second = chars_per_second
        self.char_index = 0.0
        self.total_chars_on_page = 0
        self._calculate_page_chars()

    def set_text(self, text: str) -> None:
        self._pages = self._paginate(text)
        self.page_index = 0
        self.char_index = 0.0
        self._calculate_page_chars()
        self.visible = True

    def _calculate_page_chars(self) -> None:
        if self.page_index < len(self._pages):
            self.total_chars_on_page = sum(len(line) for line in self._pages[self.page_index])
        else:
            self.total_chars_on_page = 0

    def update(self, dt: float) -> None:
        if self.char_index < self.total_chars_on_page:
            old_index = int(self.char_index)
            self.char_index += self.chars_per_second * dt
            new_index = int(self.char_index)
            
            if new_index > old_index:
                full_text = "".join(self._pages[self.page_index])
                if old_index < len(full_text):
                    revealed = full_text[old_index:new_index]
                    if any(not c.isspace() for c in revealed):
                        bleep_num = random.randint(1, 5)
                        bleep_name = f"bleep{bleep_num}"
                        
                        if bleep_name in settings.SOUNDS:
                            settings.SOUNDS[bleep_name].play()

    @property
    def is_typing(self) -> bool:
        return self.char_index < self.total_chars_on_page

    def advance(self) -> None:
        if self.is_typing:
            self.char_index = float(self.total_chars_on_page)
        else:
            super().advance()
            self.char_index = 0.0
            self._calculate_page_chars()

    def next_page(self) -> bool:
        if self.is_typing:
            self.char_index = float(self.total_chars_on_page)
            return False
            
        res = super().next_page()
        if res:
            self.char_index = 0.0
            self._calculate_page_chars()
        return res

    def previous_page(self) -> bool:
        res = super().previous_page()
        if res:
            self.char_index = 0.0
            self._calculate_page_chars()
        return res

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        pygame.draw.rect(surface, self.theme.background_color, self.rect)

        if self.theme.border_width > 0:
            pygame.draw.rect(
                surface, self.theme.border_color, self.rect, self.theme.border_width
            )

        font = self._font if self._font is not None else self.theme.font
        line_height = font.get_linesize()

        if self.page_index >= len(self._pages):
            return

        chars_to_render = int(self.char_index)
        
        for i, line in enumerate(self._pages[self.page_index]):
            if chars_to_render <= 0:
                break
                
            if len(line) <= chars_to_render:
                text_to_render = line
                chars_to_render -= len(line)
            else:
                text_to_render = line[:chars_to_render]
                chars_to_render = 0
                
            text_obj = Text(
                text_to_render,
                font,
                self.x + self.theme.padding,
                self.y + self.theme.padding + i * line_height,
                self.theme.text_color,
            )
            text_obj.render(surface)
