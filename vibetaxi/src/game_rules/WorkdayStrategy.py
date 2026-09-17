from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class WorkdayStrategy(BaseRuleStrategy):
    def __init__(self, time_limit: float = 20.0, money: float = 0.0, day: int = 1):
        super().__init__()
        self.time_remaining = time_limit
        self.money = money
        self.day = day

    def update(self, dt: float):
        if self.game_over:
            return
            
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True

    def get_start_text(self) -> str:
        return f"Day {self.day}"

    def on_passenger_delivered(self, distance: float):
        # Base gain decays depending on the day
        base_gain = max(2.0, 10.0 - (self.day - 1) * 1.5)
        earned = base_gain + (distance / 100.0)
        self.money += earned
        
        self.trigger_popup_text(f"+${earned:.2f}", (50, 255, 50))

    def render_ui(self, surface, font, x, y):
        from gale.text import render_text
        import settings
        
        # Render common taximeter
        self._render_taximeter(surface, x, y)
        
        # Use bigger font for the label
        big_font = settings.FONTS["medium"]
        render_text(surface, f"Money: ${self.money:.2f}", big_font, x, y + 45, (100, 255, 100), shadowed=True)
        
        self._render_popup_text(surface)
