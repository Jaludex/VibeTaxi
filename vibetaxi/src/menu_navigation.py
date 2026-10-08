import time
import gale.ui.container

def spatial_move_focus(self, direction):
    focusable = self._focusable_children()
    if not focusable:
        return False
        
    dx, dy = direction
    current = self._focused_child()
    
    if current is None:
        self._focus_only(focusable[0])
        return True
        
    best_child = None
    best_score = float('inf')
    
    for child in focusable:
        if child == current: continue
        
        # calculate center of current
        cx1 = current.x + getattr(current, 'width', 0) / 2
        cy1 = current.y + getattr(current, 'height', 0) / 2
        
        # calculate center of child
        cx2 = child.x + getattr(child, 'width', 0) / 2
        cy2 = child.y + getattr(child, 'height', 0) / 2
        
        vx = cx2 - cx1
        vy = cy2 - cy1
        
        dot = vx * dx + vy * dy
        
        # Must be generally in the right direction
        if dot > 0:
            dist = (vx**2 + vy**2)**0.5
            cross = abs(vx * dy - vy * dx)
            # Penalty for being off-axis
            score = dist + cross * 2
            
            if score < best_score:
                best_score = score
                best_child = child
                
    if best_child:
        self._focus_only(best_child)
        return True
        
    # If no child found in that direction, don't move
    return False

gale.ui.container.Container._move_focus = spatial_move_focus

_axis_state = {"x": 0, "y": 0}
_last_nav_time = 0

def handle_menu_navigation(ui, input_id, input_data):
    global _axis_state, _last_nav_time
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
