class BaseRuleStrategy:
    def __init__(self):
        self.game_over = False

    def update(self, dt: float):
        pass

    def on_passenger_delivered(self, distance: float):
        pass

    def render_ui(self, surface, font, x, y):
        # Allow the strategy to render its own stats (time, score, money)
        pass
        
    def _render_taximeter(self, surface, x, y):
        from gale.text import render_text
        import settings
        
        taximeter_img = settings.TEXTURES.get("taximeter")
        if taximeter_img:
            surface.blit(taximeter_img, (x, y))
            
        time_remaining = getattr(self, "time_remaining", 0)
        minutes = int(time_remaining) // 60
        seconds = int(time_remaining) % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        led_color = (200, 45, 72)
        
        render_text(
            surface, "TIME", settings.FONTS["minecraft"],
            x + 40, y + 7, (170, 170, 170), center=True
        )
        
        render_text(
            surface, time_str, settings.FONTS["led"],
            x + 40, y + 17, led_color, center=True
        )
