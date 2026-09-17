from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class WorkdayStrategy(BaseRuleStrategy):
    def __init__(self, time_limit: float = 300.0):
        super().__init__()
        self.time_remaining = time_limit
        self.money = 0.0

    def update(self, dt: float):
        if self.game_over:
            return
            
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True

    def on_passenger_delivered(self, distance: float):
        # Ganancia base + bono por distancia
        earned = 10.0 + (distance / 100.0)
        self.money += earned

    def render_ui(self, surface, font, x, y):
        from gale.text import render_text
        import settings
        
        minutes = int(self.time_remaining) // 60
        seconds = int(self.time_remaining) % 60
        time_str = f"Time: {minutes:02d}:{seconds:02d}"
        
        render_text(surface, time_str, font, x, y, (255, 255, 255), shadowed=True)
        render_text(surface, f"Money: ${self.money:.2f}", font, x, y + 25, (100, 255, 100), shadowed=True)
