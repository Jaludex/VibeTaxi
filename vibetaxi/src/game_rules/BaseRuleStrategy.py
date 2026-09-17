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
