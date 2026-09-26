import re

def modify_file(filepath, replacements):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if 'from src.i18n import tr' not in content:
        content = "from src.i18n import tr\n" + content
        
    for search, replacement in replacements.items():
        content = content.replace(search, replacement)
        
    with open(filepath, 'w') as f:
        f.write(content)

modify_file('vibetaxi/src/states/game/Menus/ConfirmationState.py', {
    '"Yes"': 'tr("btn_yes", default="Yes")',
    '"No"': 'tr("btn_no", default="No")',
    'def enter(self, enter_params: Optional[Dict[str, Any]] = None):': 'def enter(self, enter_params=None):'
})

modify_file('vibetaxi/src/states/game/Gameplay/PauseState.py', {
    '"Paused"': 'tr("pause_title", default="Paused")',
    '"Continue"': 'tr("btn_resume", default="Continue")',
    '"Main Menu"': 'tr("btn_exit_menu", default="Main Menu")',
    '"Quit Game"': 'tr("btn_quit_desktop", default="Quit Game")',
    'def enter(self, enter_params: Optional[Dict[str, Any]] = None):': 'def enter(self, enter_params=None):'
})

