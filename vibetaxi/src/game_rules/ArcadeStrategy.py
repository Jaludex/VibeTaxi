from src.i18n import tr
from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class ArcadeStrategy(BaseRuleStrategy):
    def __init__(self, start_time: float = 120.0, passengers_delivered: int = 0, score: int = 0):
        super().__init__()
        self.time_remaining = start_time
        self.passengers_delivered = passengers_delivered
        self.score = score
        self.display_score = float(score)
        
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
        return tr("mode_arcade_initial_text")

    def on_passenger_delivered(self, passenger, distance: float):
        import settings
        self.passengers_delivered += 1
        
        # Base time gained and score
        time_gained = 8.0
        base_score = settings.ARCADE_BASE_SCORE
        
        # Expected time and bonuses
        expected_time = max(5.0, distance / 100.0)
        
        time_bonus = 0.0
        score_time_bonus = 0
        if getattr(passenger, "time_riding", 999.0) < expected_time * 0.8:
            time_bonus = 5.0 # Fast arrival time bonus
            score_time_bonus = settings.ARCADE_TIME_BONUS_SCORE
            
        safety_bonus = 0.0
        score_safety_bonus = 0
        if getattr(passenger, "damage_taken", 1.0) == 0.0:
            safety_bonus = 3.0 # Perfect safety time bonus
            score_safety_bonus = settings.ARCADE_SAFETY_BONUS_SCORE
            
        total_time_gained = time_gained + time_bonus + safety_bonus
        self.time_remaining += total_time_gained
        
        total_score_gained = base_score + score_time_bonus + score_safety_bonus
        self.score += total_score_gained
        
        from gale.timer import Timer
        Timer.tween(1.0, [(self, {"display_score": float(self.score)})], ease_function_name="out_cubic")
        
        # Score popup next to label
        self.score_popup_text = f"+{total_score_gained} pts"
        if time_bonus > 0 or safety_bonus > 0:
            reasons = []
            if time_bonus > 0: reasons.append(tr("bonus_fast", default="Fast!"))
            if safety_bonus > 0: reasons.append(tr("bonus_safe", default="Safe!"))
            self.score_popup_text += f"\n({', '.join(reasons)})"
            
        self.score_popup_alpha = 0.0
        self.score_popup_y_offset = 0.0
        
        def fade_out_score():
            Timer.tween(0.5, [(self, {"score_popup_alpha": 0.0})])
            
        Timer.tween(0.3, [(self, {"score_popup_alpha": 255.0, "score_popup_y_offset": -20.0})], ease_function_name="out_cubic", on_finish=lambda: Timer.after(1.0, fade_out_score))
        
        # Show time bonus in center popup
        popup_text = f"+{int(total_time_gained)}s"
        self.trigger_popup_text(popup_text, (255, 255, 50))

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
        
        val_str = tr("hud_score_value", score=int(getattr(self, "display_score", self.score)))
        lbl_str = tr("hud_score_label")
        
        center_x = x + 40
        render_text(surface, val_str, val_font, center_x, y + 55, (255, 200, 50), shadowed=True, center=True)
        render_text(surface, lbl_str, lbl_font, center_x, y + 80, (255, 200, 50), shadowed=True, center=True)
        
        if getattr(self, "score_popup_alpha", 0) > 0:
            text_w, _ = val_font.size(val_str)
            popup_x = center_x + (text_w / 2) + 10
            popup_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            
            lines = self.score_popup_text.split('\n')
            for i, line in enumerate(lines):
                render_text(popup_surf, line, settings.FONTS["minecraft"], popup_x, y + 45 + self.score_popup_y_offset + i*15, (255, 255, 50), shadowed=True)
                
            popup_surf.set_alpha(int(self.score_popup_alpha))
            surface.blit(popup_surf, (0, 0))
        
        self._render_popup_text(surface)

    def on_game_over(self, state_machine, taxi):
        import settings
        has_records = settings.SAVE_MANAGER.exists("records")
        records = settings.SAVE_MANAGER.load("records") if has_records else {"workday": [], "arcade": []}
        
        def show_game_over(record_data=None):
            from src.states.game.Gameplay.GameOverState import GameOverState
            reason = "Time is up!" if self.time_remaining <= 0 else "Your taxi was destroyed!"
            state_machine.push(GameOverState(state_machine, reason=reason, record_data=record_data))

        score = self.score
        record_data = None
        if score > 0 and (len(records["arcade"]) < 10 or score > records["arcade"][-1]["score"]):
            record_data = {"mode": "arcade", "score": score, "records": records}
            
        show_game_over(record_data)
