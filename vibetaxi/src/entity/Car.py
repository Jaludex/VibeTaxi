import settings
from src.entity.Entity import Entity

class Car(Entity):
    def __init__(self, x, y, definition):
        super().__init__(x, y, definition) 
        
        self.speed = 0
        self.angle = 0
        self.health = self.def_data["base_health"]
        
        self.max_speed = self.def_data["max_speed"]
        self.acceleration = self.def_data.get("acceleration", 200)
        self.friction = self.def_data.get("friction", 300)
        self.turn_speed = self.def_data.get("turn_speed", 4.0)
        
        self.target_x = x
        self.target_y = y