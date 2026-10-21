import time

_axis_state = {"x": 0, "y": 0}
_last_nav_time = 0

def handle_menu_navigation(ui, input_id, input_data):
    global _axis_state, _last_nav_time
    import settings
    from gale.input_handler import KeyboardData, GamepadButtonData, GamepadAxisData, MouseMotionData, MouseClickData
    
    if isinstance(input_data, (GamepadButtonData, GamepadAxisData)):
        settings.LAST_INPUT_DEVICE = "gamepad"
    elif isinstance(input_data, KeyboardData):
        settings.LAST_INPUT_DEVICE = "keyboard"
    elif isinstance(input_data, (MouseMotionData, MouseClickData)):
        settings.LAST_INPUT_DEVICE = "mouse"

    if not ui or not ui.root:
        return False
        
    current_time = time.time()
    nav_cooldown = 0.25  # 250ms cooldown for analog stick navigation
    
    # Handle analog stick navigation
    if input_id in ("steer_x", "steer_y"):
        val = input_data.value
        axis = "x" if input_id == "steer_x" else "y"
        
        if abs(val) < 0.5:
            _axis_state[axis] = 0
            return False
            
        direction = 1 if val > 0 else -1
        
        if _axis_state[axis] != direction or (current_time - _last_nav_time) > nav_cooldown:
            _axis_state[axis] = direction
            _last_nav_time = current_time
            if axis == "x":
                ui.root.on_navigate((direction, 0))
            else:
                ui.root.on_navigate((0, direction))
            return True
        return False

    # Handle discrete button navigation
    is_pressed = getattr(input_data, "pressed", False)
    if not is_pressed:
        return False
        
    if input_id in ("move_up", "vol-up"):
        ui.root.on_navigate((0, -1))
        return True
    elif input_id in ("move_down", "vol-down"):
        ui.root.on_navigate((0, 1))
        return True
    elif input_id == "move_left":
        ui.root.on_navigate((-1, 0))
        return True
    elif input_id == "move_right":
        ui.root.on_navigate((1, 0))
        return True
    elif input_id == "confirm":
        ui.root.on_confirm()
        return True
        
    return False
