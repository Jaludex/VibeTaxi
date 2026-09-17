import pygame
from typing import Any, Dict, List, Optional
from gale.state import BaseState
from gale.timer import Timer
from gale.text import render_text
from gale.input_handler import InputData
import settings
from src.states.game.Menus.TitleScreenState import TitleScreenState


class OpeningState(BaseState):
    def enter(self, enter_params: Optional[Dict[str, Any]] = None) -> None:
        self.slides: List[Dict[str, Any]] = [
        {
            "text": "Whitebox Studio",
            "subtext": "Presents...",
            "icon": None,
            "hold_time": 1.5,
        },
        {
            "text": "A game made with <3",
            "subtext": "and lots of coffee",
            "icon": None,
            "hold_time": 1.5,
        }
        ]
        
        self.fade_in_time: float = 0.8
        self.fade_out_time: float = 0.8
        
        self._current_tween = None
        self._current_timer = None
        self._finished: bool = False
        self.current_index = 0
        self.alpha = 0.0
        self._finished = False
        self._start_slide(self.current_index)

    def _start_slide(self, index: int) -> None:
        if index >= len(self.slides):
            self._finish()
            return
            
        self.alpha = 0.0
        slide = self.slides[index]
        
        self._cancel_timers()
        
        self._current_tween = Timer.tween(
            self.fade_in_time,
            [(self, {"alpha": 255.0})],
            on_finish=lambda: self._on_fade_in_complete(slide)
        )

    def _on_fade_in_complete(self, slide: Dict[str, Any]) -> None:
        if self._finished:
            return
            
        hold = slide.get("hold_time", 1.5)
        self._current_timer = Timer.after(hold, self._start_fade_out)

    def _start_fade_out(self) -> None:
        if self._finished:
            return
            
        self._cancel_timers()
        self._current_tween = Timer.tween(
            self.fade_out_time,
            [(self, {"alpha": 0.0})],
            on_finish=self._on_fade_out_complete
        )

    def _on_fade_out_complete(self) -> None:
        if self._finished:
            return
            
        self.current_index += 1
        if self.current_index < len(self.slides):
            self._start_slide(self.current_index)
        else:
            self._finish()

    def _cancel_timers(self) -> None:
        if self._current_tween:
            self._current_tween.remove()
            self._current_tween = None
        if self._current_timer:
            self._current_timer.remove()
            self._current_timer = None

    def _finish(self) -> None:
        if self._finished:
            return
        self._finished = True
        self._cancel_timers()
        
        self.state_machine.pop()
        self.state_machine.push(TitleScreenState(self.state_machine))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if getattr(input_data, "pressed", False):
            self._finish()

    def exit(self) -> None:
        self._cancel_timers()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        
        if self.current_index >= len(self.slides):
            return
            
        slide = self.slides[self.current_index]
        
        slide_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        slide_surface.fill((0, 0, 0, 0))
        
        center_x = settings.VIRTUAL_WIDTH / 2
        center_y = settings.VIRTUAL_HEIGHT / 2
        
        icon = slide.get("icon")
        icon_surface = None
        if isinstance(icon, str) and icon in settings.TEXTURES:
            icon_surface = settings.TEXTURES[icon]
        elif isinstance(icon, pygame.Surface):
            icon_surface = icon
            
        text_y_offset = 0
        if icon_surface:
            icon_rect = icon_surface.get_rect(center=(center_x, center_y - 25))
            slide_surface.blit(icon_surface, icon_rect.topleft)
            text_y_offset = 25
            
        title_text = slide.get("text", "")
        if title_text:
            render_text(
                slide_surface,
                title_text,
                settings.FONTS["big"],
                center_x,
                center_y + text_y_offset - 10,
                (255, 255, 255),
                center=True
            )
            
        subtext = slide.get("subtext", "")
        if subtext:
            render_text(
                slide_surface,
                subtext,
                settings.FONTS["minecraft"],
                center_x,
                center_y + text_y_offset + 18,
                (180, 180, 180),
                center=True
            )
            
        slide_surface.set_alpha(int(max(0.0, min(255.0, self.alpha))))
        surface.blit(slide_surface, (0, 0))
