from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class WorkdayStrategy(BaseRuleStrategy):
    def __init__(self, time_limit: float = 120.0, money: float = 0.0, day: int = 1):
        super().__init__()
        self.time_remaining = time_limit
        self.money = money
        self.day = day
        self.fee = 80.0 + (self.day - 1) * 15.0

    def update(self, dt: float):
        if self.game_over:
            return
            
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True

    def get_start_text(self) -> str:
        return f"Day {self.day}\nToday's fee: ${self.fee:.2f}"

    def on_passenger_delivered(self, distance: float):
        # Base gain is constant now
        base_gain = 10.0
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

    def on_game_over(self, state_machine, taxi):
        if taxi.health <= 0:
            from src.states.game.Gameplay.GameOverState import GameOverState
            state_machine.push(GameOverState(state_machine))
        else:
            if self.money >= self.fee:
                self.money -= self.fee
                from src.states.game.Gameplay.EndOfDayState import EndOfDayState
                state_machine.push(EndOfDayState(
                    state_machine,
                    money=self.money,
                    health=taxi.health,
                    max_health=taxi.max_health,
                    day=self.day
                ))
            else:
                from src.states.game.Gameplay.GameOverState import GameOverState
                state_machine.push(GameOverState(
                    state_machine,
                    reason=f"You couldn't pay today's fee: ${self.fee:.2f}"
                ))
