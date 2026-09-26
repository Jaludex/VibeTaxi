from src.i18n import tr
from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class WorkdayStrategy(BaseRuleStrategy):
    def __init__(self, time_limit: float = 120.0, money: float = 0.0, day: int = 1, is_loaded_run: bool = False):
        super().__init__()
        self.time_remaining = time_limit
        self.money = money
        self.display_money = float(money)
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
        return tr("mode_workday_initial_text", day=self.day, fee=self.fee)

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
        
        from gale.timer import Timer
        Timer.tween(1.0, [(self, {"display_money": float(self.money)})], ease_function_name="out_cubic")
        
        # Show bonuses in popup next to label
        self.money_popup_text = f"+${earned:.2f}"
        if time_bonus > 0 or safety_bonus > 0:
            reasons = []
            if time_bonus > 0: reasons.append(tr("bonus_fast", default="Fast!"))
            if safety_bonus > 0: reasons.append(tr("bonus_safe", default="Safe!"))
            self.money_popup_text += f"\n({', '.join(reasons)})"
            
        self.money_popup_alpha = 0.0
        self.money_popup_y_offset = 0.0
        
        def fade_out_money():
            Timer.tween(0.5, [(self, {"money_popup_alpha": 0.0})])
            
        Timer.tween(0.3, [(self, {"money_popup_alpha": 255.0, "money_popup_y_offset": -20.0})], ease_function_name="out_cubic", on_finish=lambda: Timer.after(1.0, fade_out_money))

    def render_ui(self, surface, font, x, y):
        from gale.text import render_text
        import settings
        import pygame
        
        self.ui.render(surface)
        self.passenger_hud.render_portrait(surface)
        
        # Render common taximeter
        self._render_taximeter(surface, x, y)
        
        val_font = settings.FONTS["big"]
        lbl_font = settings.FONTS["medium"]
        
        val_str = tr("hud_money_value", money=getattr(self, "display_money", self.money))
        lbl_str = tr("hud_money_label")
        
        center_x = x + 40
        render_text(surface, val_str, val_font, center_x, y + 55, (100, 255, 100), shadowed=True, center=True)
        render_text(surface, lbl_str, lbl_font, center_x, y + 80, (100, 255, 100), shadowed=True, center=True)
        
        if getattr(self, "money_popup_alpha", 0) > 0:
            text_w, _ = val_font.size(val_str)
            popup_x = center_x + (text_w / 2) + 10
            popup_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            
            lines = self.money_popup_text.split('\n')
            for i, line in enumerate(lines):
                render_text(popup_surf, line, settings.FONTS["minecraft"], popup_x, y + 45 + self.money_popup_y_offset + i*15, (50, 255, 50), shadowed=True)
                
            popup_surf.set_alpha(int(self.money_popup_alpha))
            surface.blit(popup_surf, (0, 0))
        
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
            show_game_over(reason="Your taxi was destroyed!")
        else:
            if self.money >= self.fee:
                self.money -= self.fee
                show_end_of_day()
            else:
                show_game_over(reason=f"You couldn't pay today's fee: ${self.fee:.2f}")
