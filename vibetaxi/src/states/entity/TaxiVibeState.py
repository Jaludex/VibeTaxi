import math
from src.states.entity.TaxiDriveState import TaxiDriveState
from src import commands

class TaxiVibeState(TaxiDriveState):
    def enter(self, **kwargs):
        # 1. Guardamos valores originales
        self.original_max_speed = self.entity.max_speed
        self.original_turn_speed = self.entity.turn_speed

        self.entity.max_speed *= 1.4  
        self.entity.is_drifting = False

        self.slide_vx = self.entity.vx
        self.slide_vy = self.entity.vy
        
        super().enter(**kwargs)

    def exit(self):
        self.entity.max_speed = self.original_max_speed
        self.entity.turn_speed = self.original_turn_speed
        self.entity.is_drifting = False

    def update(self, dt):
        if getattr(self.entity, "is_drifting", False):
            self.entity.turn_speed = self.original_turn_speed * 2.2
        else:
            self.entity.turn_speed = self.original_turn_speed

        super().update(dt)

        ideal_vx = self.entity.vx
        ideal_vy = self.entity.vy

        if getattr(self.entity, "is_drifting", False):
            grip = 2.0  
        else:
            grip = 12.0 

        # Interpolación (Lerp): Acercamos la velocidad real a la ideal suavemente
        self.slide_vx += (ideal_vx - self.slide_vx) * grip * dt
        self.slide_vy += (ideal_vy - self.slide_vy) * grip * dt

        if getattr(self.entity, "is_drifting", False):
            current_speed = math.hypot(self.slide_vx, self.slide_vy)
            ideal_speed = abs(self.entity.speed)
            
            if current_speed > 0.1 and ideal_speed > 0.1:
                ratio = (ideal_speed * 0.95) / current_speed 
                if ratio > 1.0:
                    self.slide_vx *= ratio
                    self.slide_vy *= ratio

        self.entity.vx = self.slide_vx
        self.entity.vy = self.slide_vy

    def on_input(self, input_id, input_data):
        super().on_input(input_id, input_data)

        # Input del derrape
        if input_id == "drift":
            if input_data.pressed:
                commands.DRIFT.execute(self.entity)
            else:
                commands.STOP_DRIFT.execute(self.entity)