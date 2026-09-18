import settings
from typing import Dict, Any, Optional

from src.states.game.Menus.MessageBoxState import MessageBoxState
from src.states.game.Menus.TitleScreenState import TitleScreenState

class GameOverState(MessageBoxState):
    def __init__(self, state_machine: Any, reason: Optional[str] = None, record_data: Optional[Dict] = None) -> None:
        message = reason if reason else "Click OK to exit"
        
        def on_close():
            if record_data:
                from src.states.game.Gameplay.NewRecordState import NewRecordState
                
                def go_to_title():
                    while len(state_machine.states) > 0:
                        state_machine.pop()
                    state_machine.push(TitleScreenState(state_machine))
                    
                state_machine.push(NewRecordState(
                    state_machine,
                    record_data["mode"],
                    record_data["score"],
                    record_data["records"],
                    go_to_title
                ))
            else:
                while len(state_machine.states) > 0:
                    state_machine.pop()
                state_machine.push(TitleScreenState(state_machine))
                
        super().__init__(state_machine, "GAME OVER", message, on_close)

    def enter(self, enter_params: Optional[Dict[str, Any]] = None):
        super().enter(enter_params)
        if "game_over" in settings.SOUNDS:
            settings.SOUNDS["game_over"].play()
