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

    def on_passenger_delivered(self, distance: float):
        self.passengers_delivered += 1
        
        # Otorga algo de tiempo en función de la distancia (ej. 1 segundo por cada 200 pixeles, max 15 segs)
        time_bonus = min(15.0, distance / 200.0)
        self.time_remaining += time_bonus

    def render_ui(self, surface, font, x, y):
        from gale.text import render_text
        
        # Render common taximeter
        self._render_taximeter(surface, x, y)
            
        render_text(surface, f"Score: {self.passengers_delivered}", font, x, y + 35, (255, 200, 50), shadowed=True)
