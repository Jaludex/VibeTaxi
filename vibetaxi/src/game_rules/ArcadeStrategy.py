from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class ArcadeStrategy(BaseRuleStrategy):
    def __init__(self, start_time: float = 120.0, passengers_delivered: int = 0):
        super().__init__()
        self.time_remaining = start_time
        self.passengers_delivered = passengers_delivered
        
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
        
        if self.game_over:
            return
            
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True

    def get_start_text(self) -> str:
        return "Go get them!"

    def on_passenger_delivered(self, passenger, distance: float):
        self.passengers_delivered += 1
        
        # Base time gained
        time_gained = 15.0
        
        # Expected time and bonuses
        expected_time = max(5.0, distance / 100.0)
        
        time_bonus = 0.0
        if getattr(passenger, "time_riding", 999.0) < expected_time * 0.8:
            time_bonus = 5.0 # Fast arrival bonus
            
        safety_bonus = 0.0
        if getattr(passenger, "damage_taken", 1.0) == 0.0:
            safety_bonus = 3.0 # Perfect safety bonus
            
        total_time_gained = time_gained + time_bonus + safety_bonus
        self.time_remaining += total_time_gained
        
        # Show bonuses in popup
        popup_text = f"+{int(total_time_gained)}s"
        if time_bonus > 0 or safety_bonus > 0:
            reasons = []
            if time_bonus > 0: reasons.append("Fast!")
            if safety_bonus > 0: reasons.append("Safe!")
            popup_text += f" ({', '.join(reasons)})"
            
        self.trigger_popup_text(popup_text, (255, 255, 50))

    def render_ui(self, surface, font, x, y):
        from gale.text import render_text
        import settings
        
        self.ui.render(surface)
        self.passenger_hud.render_portrait(surface)
        
        # Render common taximeter
        self._render_taximeter(surface, x, y)
            
        big_font = settings.FONTS["medium"]
        render_text(surface, f"Score: {self.passengers_delivered}", big_font, x, y + 45, (255, 200, 50), shadowed=True)
        
        self._render_popup_text(surface)

    def on_game_over(self, state_machine, taxi):
        import settings
        has_records = settings.SAVE_MANAGER.exists("records")
        records = settings.SAVE_MANAGER.load("records") if has_records else {"workday": [], "arcade": []}
        
        def show_game_over(record_data=None):
            from src.states.game.Gameplay.GameOverState import GameOverState
            reason = "Time is up!" if self.time_remaining <= 0 else "Your taxi was destroyed!"
            state_machine.push(GameOverState(state_machine, reason=reason, record_data=record_data))

        score = self.passengers_delivered
        record_data = None
        if score > 0 and (len(records["arcade"]) < 10 or score > records["arcade"][-1]["score"]):
            record_data = {"mode": "arcade", "score": score, "records": records}
            
        show_game_over(record_data)
