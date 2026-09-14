import math
from src.states.entity.BaseEntityState import BaseEntityState

class PassengerWalkState(BaseEntityState):
    def enter(self, **kwargs):
        self.entity.target = kwargs.get("target")
        self.entity.on_arrival = kwargs.get("on_arrival")
        self.entity.change_animation("walk")

    def update(self, dt):
        if not self.entity.target:
            return

        if hasattr(self.entity.target, "x") and hasattr(self.entity.target, "y"):
            target_x, target_y = self.entity.target.x, self.entity.target.y
        else:
            target_x, target_y = self.entity.target

        dx = target_x - self.entity.x
        dy = target_y - self.entity.y
        distance = math.hypot(dx, dy)
        
        self.entity.flipped = dx < 0
        
        if distance < 5.0:
            self.entity.vx = 0
            self.entity.vy = 0
            if self.entity.on_arrival:
                self.entity.on_arrival()
        else:
            move_speed = 100 * dt
            self.entity.x += (dx / distance) * move_speed
            self.entity.y += (dy / distance) * move_speed