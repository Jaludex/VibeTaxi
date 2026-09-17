from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class ArcadeStrategy(BaseRuleStrategy):
    def __init__(self, start_time: float = 120.0):
        super().__init__()
        self.time_remaining = start_time
        self.passengers_delivered = 0

    def update(self, dt: float):
        if self.game_over:
            return
            
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True

    def get_start_text(self) -> str:
        return "Go get them!"

    def on_passenger_delivered(self, distance: float):
        self.passengers_delivered += 1
        
        # Grants some time based on distance (e.g., 1 second per 200 pixels, max 15 secs)
        time_bonus = min(15.0, distance / 200.0)
        self.time_remaining += time_bonus
        
        self.trigger_popup_text(f"+{time_bonus:.1f}s", (255, 255, 50))

    def render_ui(self, surface, font, x, y):
        from gale.text import render_text
        import settings
        
        # Render common taximeter
        self._render_taximeter(surface, x, y)
            
        big_font = settings.FONTS["medium"]
        render_text(surface, f"Score: {self.passengers_delivered}", big_font, x, y + 45, (255, 200, 50), shadowed=True)
        
        self._render_popup_text(surface)

    def on_game_over(self, state_machine, taxi):
        from src.states.game.Gameplay.GameOverState import GameOverState
        state_machine.push(GameOverState(state_machine))
