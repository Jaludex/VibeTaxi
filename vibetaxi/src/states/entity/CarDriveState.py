import math
import pygame
from src.states.entity.BaseEntityState import BaseEntityState

class CarDriveState(BaseEntityState):
    def update(self, dt):
        dx = self.entity.target_x - self.entity.x
        dy = self.entity.target_y - self.entity.y
        target_angle = math.atan2(dy, dx)
        
        distance = math.hypot(dx, dy)
        slowdown_radius = 150.0  
        
        if distance < 15: 
            target_max_speed = 0
        elif distance < slowdown_radius:
            target_max_speed = self.entity.max_speed * (distance / slowdown_radius)
        else:
            target_max_speed = self.entity.max_speed
        
        speed_ratio = self.entity.speed / self.entity.max_speed if self.entity.max_speed > 0 else 1.0
        
        if self.entity.speed < 30:
            turn_multiplier = (self.entity.speed / 30.0) 
        else:
            turn_multiplier = 1.5 - (0.9 * speed_ratio)
            
        dynamic_turn_speed = self.entity.turn_speed * turn_multiplier
        
        angle_diff = (target_angle - self.entity.angle + math.pi) % (2 * math.pi) - math.pi
        turn_amount = dynamic_turn_speed * dt
        
        if abs(angle_diff) < turn_amount:
            self.entity.angle = target_angle
        else:
            if angle_diff > 0:
                self.entity.angle += turn_amount
            else:
                self.entity.angle -= turn_amount

        self.entity.angle = (self.entity.angle + math.pi) % (2 * math.pi) - math.pi
        
        is_moving = getattr(self.entity, "is_accelerating", True)
        is_braking = getattr(self.entity, "is_braking", False)
        
        current_friction = self.entity.friction * 3.0 if is_braking else self.entity.friction

        if is_moving and distance >= 15 and not is_braking:
            if self.entity.speed < target_max_speed:
                self.entity.speed += self.entity.acceleration * dt
                if self.entity.speed > target_max_speed:
                    self.entity.speed = target_max_speed
            elif self.entity.speed > target_max_speed:
                self.entity.speed -= current_friction * dt
                if self.entity.speed < target_max_speed:
                    self.entity.speed = target_max_speed
        else:
            self.entity.speed -= current_friction * dt
            if self.entity.speed <= 0:
                self.entity.speed = 0
                self.state_machine.change('idle')
                return

        self.entity.vx = math.cos(self.entity.angle) * self.entity.speed
        self.entity.vy = math.sin(self.entity.angle) * self.entity.speed