from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class WorkdayStrategy(BaseRuleStrategy):
    def __init__(self, time_limit: float = 120.0, money: float = 0.0, day: int = 1, is_loaded_run: bool = False):
        super().__init__()
        self.time_remaining = time_limit
        self.money = money
        self.day = day
        self.is_loaded_run = is_loaded_run
        self.fee = 80.0 + (self.day - 1) * 15.0
        
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

    def to_dict(self) -> dict:
        return {
            "time_limit": self.time_remaining,
            "money": self.money,
            "day": self.day
        }

    @classmethod
    def load_dict(cls, data: dict):
        return cls(
            time_limit=data.get("time_limit", 120.0),
            money=data.get("money", 0.0),
            day=data.get("day", 1),
            is_loaded_run=True
        )

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
        return f"Day {self.day}\nToday's fee: ${self.fee:.2f}"

    def on_passenger_delivered(self, passenger, distance: float):
        # Base gain
        base_gain = 10.0
        earned = base_gain + (distance / 100.0)
        
        # Calculate expected time based on distance (assuming average speed)
        # Assuming speed of ~100 units/sec, so expected time = distance / 100
        expected_time = max(5.0, distance / 100.0)
        
        time_bonus = 0.0
        if getattr(passenger, "time_riding", 999.0) < expected_time * 0.8:
            time_bonus = 5.0 # Fast arrival bonus
            
        safety_bonus = 0.0
        if getattr(passenger, "damage_taken", 1.0) == 0.0:
            safety_bonus = 3.0 # Perfect safety bonus
            
        earned += time_bonus + safety_bonus
        self.money += earned
        
        # Show bonuses in popup
        popup_text = f"+${earned:.2f}"
        if time_bonus > 0 or safety_bonus > 0:
            reasons = []
            if time_bonus > 0: reasons.append("Fast!")
            if safety_bonus > 0: reasons.append("Safe!")
            popup_text += f" ({', '.join(reasons)})"
            
        self.trigger_popup_text(popup_text, (50, 255, 50))

    def render_ui(self, surface, font, x, y):
        from gale.text import render_text
        import settings
        
        self.ui.render(surface)
        
        # Render common taximeter
        self._render_taximeter(surface, x, y)
        
        # Use bigger font for the label
        big_font = settings.FONTS["medium"]
        render_text(surface, f"Money: ${self.money:.2f}", big_font, x, y + 45, (100, 255, 100), shadowed=True)
        
        self._render_popup_text(surface)

    def on_game_over(self, state_machine, taxi):
        import settings
        has_records = settings.SAVE_MANAGER.exists("records")
        records = settings.SAVE_MANAGER.load("records") if has_records else {"workday": [], "arcade": []}
        
        def delete_save_if_loaded():
            if getattr(self, "is_loaded_run", False) and settings.SAVE_MANAGER.exists("workday_save"):
                settings.SAVE_MANAGER.delete("workday_save")

        def get_record_data(score):
            if score > 0 and (len(records["workday"]) < 10 or score > records["workday"][-1]["score"]):
                return {"mode": "workday", "score": score, "records": records}
            return None

        def show_game_over(reason=None):
            delete_save_if_loaded()
            from src.states.game.Gameplay.GameOverState import GameOverState
            state_machine.push(GameOverState(state_machine, reason=reason, record_data=get_record_data(self.day)))

        def show_end_of_day():
            from src.states.game.Gameplay.EndOfDayState import EndOfDayState
            state_machine.push(EndOfDayState(
                state_machine,
                money=self.money,
                health=taxi.health,
                max_health=taxi.max_health,
                day=self.day,
                is_loaded_run=self.is_loaded_run
            ))

        if taxi.health <= 0:
            show_game_over()
        else:
            if self.money >= self.fee:
                self.money -= self.fee
                show_end_of_day()
            else:
                show_game_over(reason=f"You couldn't pay today's fee: ${self.fee:.2f}")
