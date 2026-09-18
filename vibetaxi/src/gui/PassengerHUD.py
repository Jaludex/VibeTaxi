import pygame
import settings
import random
from gale.ui.container import Container
from gale.ui.panel import Panel
from gale.ui.label import Label
from gale.ui.text_box import TextBox
from gale.ui.progress_bar import ProgressBar
from gale.ui.theme import Theme
from gale.timer import Timer
from src.definitions.comfort import COMFORT_RULES
class PassengerHUD:
    def __init__(self):
        # 1. Progress Bar (Top-Right: 20px from top and 20px from right)
        self.bar_width = 130
        self.bar_height = 20
        self.bar_on_x = settings.VIRTUAL_WIDTH - self.bar_width - 20
        self.bar_off_x = settings.VIRTUAL_WIDTH + 20
        self.bar_y = 20
        self._bar_x = self.bar_off_x

        # 2. Dialogue Box (Middle-Right: vertically centered, 20px from right)
        self.dialogue_width = 200
        self.dialogue_height = 60
        self.dialogue_on_x = settings.VIRTUAL_WIDTH - self.dialogue_width - 20
        self.dialogue_off_x = settings.VIRTUAL_WIDTH + 20
        self.dialogue_y = (settings.VIRTUAL_HEIGHT - self.dialogue_height) // 2
        self._dialogue_x = self.dialogue_off_x

        # Themes
        self.bar_theme = Theme(
            font=settings.FONTS["minecraft"],
            text_color=pygame.Color(255, 220, 100),
            background_color=pygame.Color(20, 22, 30, 225),
            border_color=pygame.Color(220, 190, 80),
            border_width=1,
            padding=4,
        )

        self.dialogue_theme = Theme(
            font=settings.FONTS["minecraft"],
            text_color=pygame.Color(240, 240, 245),
            background_color=pygame.Color(24, 26, 36, 235),
            border_color=pygame.Color(130, 140, 170),
            border_width=1,
            padding=4,
        )

        self.tb_theme = Theme(
            font=settings.FONTS["minecraft"],
            text_color=pygame.Color(240, 240, 245),
            background_color=pygame.Color(32, 35, 48, 0),
            border_color=pygame.Color(0, 0, 0, 0),
            border_width=0,
            padding=2,
        )

        self.pb_theme = Theme(
            background_color=pygame.Color(15, 15, 20),
            border_color=pygame.Color(90, 95, 110),
            border_width=1,
            accent_color=pygame.Color(50, 210, 90),
        )

        # Bar Widgets
        self.bar_panel = Panel(self._bar_x, self.bar_y, self.bar_width, self.bar_height, theme=self.bar_theme)
        self.bar_label = Label(self._bar_x + 6, self.bar_y + 6, "VIBE", theme=self.bar_theme)
        self.progress_bar = ProgressBar(
            self._bar_x + 36,
            self.bar_y + 6,
            self.bar_width - 42,
            8,
            value=50,
            max_value=100,
            color=pygame.Color(50, 210, 90),
            theme=self.pb_theme,
        )

        # Dialogue Widgets
        self.dialogue_panel = Panel(
            self._dialogue_x,
            self.dialogue_y,
            self.dialogue_width,
            self.dialogue_height,
            theme=self.dialogue_theme,
        )
        self.text_box = TextBox(
            self._dialogue_x + 6,
            self.dialogue_y + 6,
            self.dialogue_width - 12,
            self.dialogue_height - 12,
            "",
            font=settings.FONTS["minecraft"],
            lines_per_page=3,
            theme=self.tb_theme,
        )

        # 3. Portrait Window (between progress bar and dialogue box, right-aligned)
        self.portrait_width = 64
        self.portrait_height = 72
        self.portrait_on_x = settings.VIRTUAL_WIDTH - self.portrait_width - 20
        self.portrait_off_x = settings.VIRTUAL_WIDTH + 20
        # Vertically centered between bar bottom and dialogue top
        bar_bottom = self.bar_y + self.bar_height
        self.portrait_y = bar_bottom + (self.dialogue_y - bar_bottom - self.portrait_height) // 2
        self._portrait_x = float(self.portrait_off_x)
        self.portrait_surface = None

        self.portrait_theme = Theme(
            font=settings.FONTS["minecraft"],
            text_color=pygame.Color(240, 240, 245),
            background_color=pygame.Color(20, 22, 30, 225),
            border_color=pygame.Color(130, 140, 170),
            border_width=1,
            padding=0,
        )

        # Root container
        self.container = Container(
            0,
            0,
            settings.VIRTUAL_WIDTH,
            settings.VIRTUAL_HEIGHT,
            children=[
                self.bar_panel,
                self.bar_label,
                self.progress_bar,
                self.dialogue_panel,
                self.text_box,
            ],
            theme=self.bar_theme,
        )

        self.passenger = None
        self.current_text = ""
        self.last_comfort = random.randint(int(COMFORT_RULES["initial_min"]), int(COMFORT_RULES["initial_max"]))

    @property
    def portrait_x(self) -> float:
        return self._portrait_x

    @portrait_x.setter
    def portrait_x(self, val: float) -> None:
        self._portrait_x = val

    @property
    def bar_x(self) -> float:
        return self._bar_x

    @bar_x.setter
    def bar_x(self, val: float) -> None:
        self._bar_x = val
        self.bar_panel.x = val
        self.bar_label.x = val + 6
        self.progress_bar.x = val + 36

    @property
    def dialogue_x(self) -> float:
        return self._dialogue_x

    @dialogue_x.setter
    def dialogue_x(self, val: float) -> None:
        self._dialogue_x = val
        self.dialogue_panel.x = val
        self.text_box.x = val + 6

    def bind_passenger(self, passenger) -> None:
        if getattr(self, "_clear_timer", None):
            self._clear_timer.remove()
            self._clear_timer = None
            
        self.passenger = passenger
        self.last_comfort = passenger.comfort
        self.progress_bar.value = passenger.comfort
        # Load portrait (use passenger texture or fallback to test_someone)
        portrait_key = passenger.definition.get("portrait", "test_someone")
        raw_img = settings.TEXTURES.get(portrait_key)
        if raw_img:
            self.portrait_surface = pygame.transform.scale(raw_img, (self.portrait_width, self.portrait_height))
        else:
            self.portrait_surface = None
        # Slide in comfort bar and portrait
        Timer.tween(0.35, [(self, {"bar_x": self.bar_on_x})])
        Timer.tween(0.35, [(self, {"portrait_x": float(self.portrait_on_x)})])
        # Show greeting dialogue
        greeting = passenger.dialogues.get("enter", "Hello! Take me to my destination.")
        self.show_text(greeting)

    def unbind_passenger(self) -> None:
        if self.passenger is None:
            return

        comfort = self.passenger.comfort
        if comfort >= COMFORT_RULES["exit_good_threshold"]:
            farewell = self.passenger.dialogues.get("exit_good", "Excellent service!")
        else:
            farewell = self.passenger.dialogues.get("exit_bad", "Terrible ride...")

        self.show_text(farewell)
        
        if getattr(self, "_clear_timer", None):
            self._clear_timer.remove()
        self._clear_timer = Timer.after(settings.DIALOGUE_DISPLAY_TIME + 0.35, self._clear_passenger)

    def _clear_passenger(self) -> None:
        self.passenger = None
        Timer.tween(0.35, [(self, {"bar_x": self.bar_off_x})])
        Timer.tween(0.35, [(self, {"portrait_x": float(self.portrait_off_x)})])

    def update(self, dt: float) -> None:
        if self.passenger:
            # Smooth progressive change when comfort changes
            if self.passenger.comfort != self.last_comfort:
                self.last_comfort = self.passenger.comfort
                Timer.tween(0.6, [(self.progress_bar, {"value": self.passenger.comfort})])

        # Dynamic color based on current interpolated progress bar value
        val = self.progress_bar.value
        if val >= 60:
            self.progress_bar._color = pygame.Color(50, 210, 90)
        elif val >= 30:
            self.progress_bar._color = pygame.Color(230, 180, 40)
        else:
            self.progress_bar._color = pygame.Color(220, 60, 60)

    def show_text(self, text: str, duration: float = settings.DIALOGUE_DISPLAY_TIME) -> None:
        self.set_text(text)
        # Slide in from right
        Timer.tween(0.3, [(self, {"dialogue_x": self.dialogue_on_x})])
        # Auto-slide out to right after duration
        if getattr(self, "_hide_timer", None):
            self._hide_timer.remove()
        self._hide_timer = Timer.after(duration, self.hide_dialogue)

    def hide_dialogue(self) -> None:
        Timer.tween(0.3, [(self, {"dialogue_x": self.dialogue_off_x})])

    def set_text(self, text: str) -> None:
        self.current_text = text
        self.text_box._pages = self.text_box._paginate(text)
        self.text_box.page_index = 0
        self.text_box.visible = True

    def render_portrait(self, surface) -> None:
        if self._portrait_x >= self.portrait_off_x:
            return
        if self.portrait_surface is None:
            return
            
        x = int(self._portrait_x)
        y = self.portrait_y
        w = self.portrait_width
        h = self.portrait_height
        
        # Draw background panel
        bg = self.portrait_theme.background_color
        panel_rect = pygame.Rect(x, y, w, h)
        panel_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        panel_surf.fill(bg)
        surface.blit(panel_surf, (x, y))
        
        # Draw portrait image centered inside
        img_w, img_h = self.portrait_surface.get_size()
        img_x = x + (w - img_w) // 2
        img_y = y + (h - img_h) // 2
        surface.blit(self.portrait_surface, (img_x, img_y))
        
        # Draw border
        border_color = self.portrait_theme.border_color
        border_w = self.portrait_theme.border_width
        pygame.draw.rect(surface, border_color, panel_rect, border_w)