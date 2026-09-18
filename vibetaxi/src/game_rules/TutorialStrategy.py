from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class TutorialStrategy(BaseRuleStrategy):
    def __init__(self):
        super().__init__()
        self.passengers_delivered = 0
        self.invincible = True
        
        from src.gui.PassengerHUD import PassengerHUD
        from gale.ui.manager import UIManager
        import settings
        self.passenger_hud = PassengerHUD()
        self.ui = UIManager(
            self.passenger_hud.container,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT
        )
        
    def get_hud(self):
        return self.passenger_hud

    def update(self, dt: float):
        self.passenger_hud.update(dt)
        self.ui.update(dt)

    def should_respawn_passengers(self, current_count: int) -> bool:
        return False
        
    def get_start_text(self) -> str:
        return "Welcome to the tutorial!"

    def on_passenger_delivered(self, passenger, distance: float):
        self.passengers_delivered += 1
        
    def render_ui(self, surface, font, x, y):
        import settings
        from gale.text import render_text
        
        self.ui.render(surface)
        self.passenger_hud.render_portrait(surface)
        
        big_font = settings.FONTS["medium"]
        render_text(surface, "TUTORIAL", big_font, x + 40, y + 20, (100, 255, 255), center=True, shadowed=True)
        
        self._render_popup_text(surface)
