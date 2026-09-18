
from typing import Optional, Callable

# Mock Gale
class Widget:
    def __init__(self, x, y, width, height, theme=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.theme = theme
        self.visible = True
    def update(self, dt): pass

class Theme:
    padding = 2
    font = None

class TextBox(Widget):
    def __init__(self, x, y, width, height, text, font=None, lines_per_page=3, on_close=None, theme=None):
        super().__init__(x, y, width, height, theme=theme)
        self._font = font
        self.lines_per_page = lines_per_page
        self._pages = self._paginate(text)
        self.page_index = 0
    def _paginate(self, text):
        return [[text]] # Mock pagination

class TypewriterTextBox(TextBox):
    def __init__(self, *args, **kwargs):
        self.chars_per_second = kwargs.pop('chars_per_second', 40.0)
        super().__init__(*args, **kwargs)
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
                char_revealed = ""
                chars_counted = 0
                for line in self._pages[self.page_index]:
                    if old_index < chars_counted + len(line):
                        char_revealed = line[old_index - chars_counted]
                        break
                    chars_counted += len(line)
                
                if char_revealed and not char_revealed.isspace():
                    print(f"Sound! char='{char_revealed}'")

tb = TypewriterTextBox(0, 0, 100, 100, "")

print("--- First text ---")
tb.set_text("Hello World!")
for _ in range(30):
    tb.update(0.016)

print("--- Second text ---")
tb.set_text("How are you?")
for _ in range(30):
    tb.update(0.016)

