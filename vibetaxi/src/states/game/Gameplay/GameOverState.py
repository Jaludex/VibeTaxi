from src.i18n import tr
import settings
from typing import Dict, Any, Optional

from src.states.game.Menus.MessageBoxState import MessageBoxState
from src.states.game.Menus.TitleScreenState import TitleScreenState

class GameOverState(MessageBoxState):
    def __init__(self, state_machine: Any, reason: Optional[str] = None, record_data: Optional[Dict] = None, mode: str = "", score: float = 0) -> None:
        message = reason if reason else "Click OK to exit"
        
        def on_close():
            if record_data:
                from src.states.game.Gameplay.NewRecordState import NewRecordState
                
                def go_to_title():
                    while len(state_machine.states) > 0:
                        state_machine.pop()
                    state_machine.push(TitleScreenState(state_machine))
                    
                state_machine.push(NewRecordState(
                    state_machine,
                    record_data["mode"],
                    record_data["score"],
                    record_data["records"],
                    go_to_title
                ))
            else:
                while len(state_machine.states) > 0:
                    state_machine.pop()
                state_machine.push(TitleScreenState(state_machine))
                
        super().__init__(state_machine, "GAME OVER", message, on_close)
        
        # Increase panel height to fit the rank
        self.panel_height = 190
        self.panel.height = 190
        self.panel.rect.height = 190
        self.target_y = settings.VIRTUAL_HEIGHT / 2 - self.panel_height / 2
        
        self.rank_alpha = 0.0
        self.rank = None
        if mode and hasattr(settings, 'RANKS'):
            best_rank = settings.RANKS[0]
            for r in settings.RANKS:
                if mode == "workday" and score >= r["workday_min"]:
                    best_rank = r
                elif mode == "arcade" and score >= r["arcade_min"]:
                    best_rank = r
            self.rank = best_rank

    def update_ui_y(self):
        self.panel.y = self.panel_y
        self.label_title.y = self.panel_y + 12
        self.text_box.y = self.panel_y + 28
        # Move the OK button down to make room for the rank
        self.btn_ok.y = self.panel_y + 154

    def enter(self, enter_params=None):
        super().enter(enter_params)
        if "game_over" in settings.SOUNDS:
            settings.SOUNDS["game_over"].play()
            
        from gale.timer import Timer
        def show_rank():
            if self.rank:
                Timer.tween(0.4, [(self, {"rank_alpha": 255.0})])
                sound_key = self.rank.get("sound")
                if sound_key and sound_key in settings.SOUNDS:
                    settings.SOUNDS[sound_key].play()
                
        # Wait 1 second after panel finishes dropping (0.5s drop + 1s wait = 1.5s)
        Timer.after(1.5, show_rank)

    def render(self, surface):
        super().render(surface)
        from gale.text import render_text
                    # Draw Rank Label (medium)
        render_text(
            surface, 
            tr("game_over_rank_label", default="RANK"), 
            settings.FONTS["medium"], 
            settings.VIRTUAL_WIDTH / 2, 
            self.panel_y + 125, 
            (255, 255, 255), 
            center=True, 
            shadowed=True
        )
        
        if self.rank and self.rank_alpha > 0:
            import pygame
            
            # Create a transparent surface for the rank text
            rank_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            
            render_text(
                rank_surf, 
                self.rank['name'], 
                settings.FONTS["rank"], 
                settings.VIRTUAL_WIDTH / 2, 
                self.panel_y + 90, 
                self.rank["color"], 
                center=True, 
                shadowed=True
            )
            
            rank_surf.set_alpha(int(self.rank_alpha))
            surface.blit(rank_surf, (0, 0))
