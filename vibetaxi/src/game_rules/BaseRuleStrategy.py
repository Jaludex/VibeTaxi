class BaseRuleStrategy:
    def __init__(self):
        self.game_over = False

    def update(self, dt: float):
        pass

    def get_start_text(self) -> str:
        return ""

    def on_passenger_delivered(self, distance: float):
        pass

    def should_respawn_passengers(self, current_count: int) -> bool:
        return False

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

    def trigger_popup_text(self, text: str, color: tuple):
        from gale.timer import Timer
        self.popup_text = text
        self.popup_color = color
        self.popup_alpha = 0.0
        
        def fade_out():
            Timer.tween(
                0.3,
                [(self, {"popup_alpha": 0.0})],
                ease_function_name="out_cubic"
            )
            
        Timer.tween(
            0.3,
            [(self, {"popup_alpha": 255.0})],
            ease_function_name="in_cubic",
            on_finish=lambda: Timer.after(0.5, fade_out)
        )

    def _render_popup_text(self, surface):
        if getattr(self, "popup_alpha", 0) > 0:
            import settings
            import pygame
            from gale.text import render_text
            
            text_layer = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            
            render_text(
                text_layer,
                self.popup_text,
                settings.FONTS["medium"],
                settings.VIRTUAL_WIDTH // 2,
                30,
                self.popup_color,
                center=True,
                shadowed=True
            )
            
            text_layer.set_alpha(int(self.popup_alpha))
            surface.blit(text_layer, (0, 0))

    def on_game_over(self, state_machine, taxi):
        pass
