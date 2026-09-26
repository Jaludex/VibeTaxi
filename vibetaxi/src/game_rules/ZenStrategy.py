from src.i18n import tr
from src.game_rules.BaseRuleStrategy import BaseRuleStrategy

class ZenStrategy(BaseRuleStrategy):
    def __init__(self):
        super().__init__()
        self.invincible = True
        self.always_vibe = True
        
    def should_respawn_passengers(self, current_count: int) -> bool:
        return current_count < 3
        
    def get_start_text(self) -> str:
        return tr("mode_zen_initial_text")
        
    def render_ui(self, surface, font, x, y):
        import settings
        from gale.text import render_text
        
        big_font = settings.FONTS["medium"]
        render_text(surface, tr("hud_zen"), big_font, x + 40, y + 20, (200, 255, 200), center=True, shadowed=True)
        
        self._render_popup_text(surface)
