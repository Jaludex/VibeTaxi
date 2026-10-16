import settings
from src.entity.Entity import Entity

class Car(Entity):
    def __init__(self, x, y, definition):
        super().__init__(x, y, definition)

        self.angle_offset = -90
        
        self.speed = 0
        self.angle = 0
        self.health = self.def_data["base_health"]
        
        self.max_speed = self.def_data["max_speed"]
        self.acceleration = self.def_data.get("acceleration", 200)
        self.friction = self.def_data.get("friction", 300)
        self.turn_speed = self.def_data.get("turn_speed", 4.0)
        self.reverse_speed_ratio = self.def_data.get("reverse_speed_ratio", 0.5)
        
        self.target_x = x
        self.target_y = y

    def penalize_speed(self, factor: float = 0.5) -> None:
        self.speed *= factor
        if hasattr(self, "vx"):
            self.vx *= factor
        if hasattr(self, "vy"):
            self.vy *= factor
        if getattr(self, "body", None) is not None:
            try:
                vel = self.body.velocity
                self.body.velocity = (vel[0] * factor, vel[1] * factor)
            except Exception:
                pass
        sm = getattr(self, "state_machine", None)
        if sm is not None and getattr(sm, "current", None) is not None:
            curr = sm.current
            if hasattr(curr, "slide_vx"):
                curr.slide_vx *= factor
            if hasattr(curr, "slide_vy"):
                curr.slide_vy *= factor