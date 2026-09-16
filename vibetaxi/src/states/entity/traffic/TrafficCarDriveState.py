import math
import pygame
from gale.state import BaseState

class TrafficCarDriveState(BaseState):
    def __init__(self, entity, sm):
        self.entity = entity
        self.sm = sm
        self.look_ahead_distance = 60.0

    def enter(self, **kwargs):
        self.entity.is_accelerating = True
        self.entity.is_braking = False

    def update(self, dt):
        dx = self.entity.target_x - self.entity.x
        dy = self.entity.target_y - self.entity.y
        distance = math.hypot(dx, dy)
        
        # Check distance to target node
        if distance < 30.0:
            if self.entity.next_node_name and self.entity.traffic_system:
                next_pos = self.entity.traffic_system.get_node_position(self.entity.next_node_name)
                next_next = self.entity.traffic_system.get_node_next(self.entity.next_node_name)
                if next_pos:
                    self.entity.target_x, self.entity.target_y = next_pos
                    self.entity.next_node_name = next_next
                else:
                    self.entity.is_accelerating = False # No path forward
            else:
                self.entity.is_accelerating = False # End of path

        # Basic driving logic
        target_angle = math.atan2(dy, dx)
        angle_diff = (target_angle - self.entity.angle + math.pi) % (2 * math.pi) - math.pi
        
        current_spd_abs = abs(self.entity.speed)
        max_spd = self.entity.max_speed
        
        # Slow down on sharp turns
        if abs(angle_diff) > 0.5:
            max_spd *= 0.5
            
        turn_amount = self.entity.turn_speed * dt
        if abs(angle_diff) < turn_amount:
            self.entity.angle = target_angle
        else:
            self.entity.angle += turn_amount if angle_diff > 0 else -turn_amount
            
        self.entity.angle = (self.entity.angle + math.pi) % (2 * math.pi) - math.pi

        target_speed = max_spd if self.entity.is_accelerating else 0.0

        accel_rate = self.entity.acceleration * dt
        friction_rate = self.entity.friction * dt

        if self.entity.speed < target_speed:
            self.entity.speed = min(self.entity.speed + accel_rate, target_speed)
        elif self.entity.speed > target_speed:
            self.entity.speed = max(self.entity.speed - friction_rate, target_speed)

        self.entity.vx = math.cos(self.entity.angle) * self.entity.speed
        self.entity.vy = math.sin(self.entity.angle) * self.entity.speed

        if self.entity.body is not None:
            try:
                desired = pygame.math.Vector2(self.entity.vx, self.entity.vy)
                current = pygame.math.Vector2(self.entity.body.velocity)
                delta = desired - current

                pm = getattr(self.entity.body, '_pm_body', None)
                mass = getattr(pm, 'mass', 1.0) if pm is not None else 1.0

                accel_needed = delta / max(dt, 1e-6)
                force = accel_needed * mass * 0.5

                max_force = abs(self.entity.acceleration) * mass * 2.0
                if hasattr(force, 'length') and force.length() > max_force:
                    force = force.normalize() * max_force

                self.entity.body.apply_force(force.x, force.y)
                self.entity.body.angle = self.entity.angle
                self.entity.body.angular_velocity = 0.0

                pos = self.entity.body.position
                self.entity.x = float(pos.x)
                self.entity.y = float(pos.y)
            except Exception:
                self.entity.body.velocity = (self.entity.vx, self.entity.vy)
                self.entity.body.angle = self.entity.angle
                self.entity.body.angular_velocity = 0.0
                self.entity.x = self.entity.body.position.x
                self.entity.y = self.entity.body.position.y

    def exit(self):
        pass
        
    def on_input(self, input_id, input_data):
        pass
