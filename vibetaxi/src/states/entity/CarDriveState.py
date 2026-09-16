import math
import pygame
from src.states.entity.BaseEntityState import BaseEntityState

class CarDriveState(BaseEntityState):
    def update(self, dt):
        dx = self.entity.target_x - self.entity.x
        dy = self.entity.target_y - self.entity.y
        distance = math.hypot(dx, dy)
        
        is_reversing = getattr(self.entity, "is_reversing", False)
        is_accelerating = getattr(self.entity, "is_accelerating", True)
        is_braking = getattr(self.entity, "is_braking", False)
        
        dir_sign = -1 if is_reversing else 1
        target_angle = math.atan2(dy, dx) + (math.pi if is_reversing else 0)
        
        angle_diff = (target_angle - self.entity.angle + math.pi) % (2 * math.pi) - math.pi

        reverse_ratio = getattr(self.entity, "reverse_speed_ratio", 0.5)
        
        current_spd_abs = abs(self.entity.speed)
        max_spd = self.entity.max_speed * (reverse_ratio if is_reversing else 1.0)
        speed_ratio = current_spd_abs / max_spd if max_spd > 0 else 0
        turn_mult = (current_spd_abs / 30.0) if current_spd_abs < 30 else (1.5 - 0.9 * speed_ratio)
        
        # Reduce raw steering responsiveness so turns are less sharp and drift mechanics feel better
        TURN_REDUCTION = 0.6
        turn_amount = self.entity.turn_speed * turn_mult * dt * TURN_REDUCTION
        if abs(angle_diff) < turn_amount:
            self.entity.angle = target_angle
        else:
            self.entity.angle += turn_amount if angle_diff > 0 else -turn_amount
        self.entity.angle = (self.entity.angle + math.pi) % (2 * math.pi) - math.pi

        target_speed = 0.0
        if not is_reversing and distance < 15:
            target_speed = 0.0
        elif (is_accelerating or is_reversing) and not is_braking:
            speed_limit = max_spd if (is_reversing or distance >= 150) else max_spd * (distance / 150.0)
            target_speed = speed_limit * dir_sign

        accel_rate = self.entity.acceleration * dt
        friction_rate = self.entity.friction * (3.0 if is_braking else 1.0) * dt

        if abs(target_speed) > abs(self.entity.speed):
            rate = accel_rate
        else:
            rate = friction_rate

        if self.entity.speed < target_speed:
            self.entity.speed = min(self.entity.speed + rate, target_speed)
        elif self.entity.speed > target_speed:
            self.entity.speed = max(self.entity.speed - rate, target_speed)

        if self.entity.speed == 0 and not is_accelerating and not is_reversing:
            self.state_machine.change('idle')
            return

        self.entity.vx = math.cos(self.entity.angle) * self.entity.speed
        self.entity.vy = math.sin(self.entity.angle) * self.entity.speed

        if self.entity.body is not None:
            try:
                desired = pygame.math.Vector2(self.entity.vx, self.entity.vy)
                current = pygame.math.Vector2(self.entity.body.velocity)
                delta = desired - current

                pm = getattr(self.entity.body, '_pm_body', None)
                mass = getattr(pm, 'mass', 1.0) if pm is not None else 1.0

                # compute required acceleration (attempt to reach target within ~0.2s scaled by dt)
                accel_needed = delta / max(dt, 1e-6)
                force = accel_needed * mass * 0.5

                # cap force
                max_force = abs(self.entity.acceleration) * mass * 2.0
                if hasattr(force, 'length') and force.length() > max_force:
                    force = force.normalize() * max_force

                # apply force in world coords
                self.entity.body.apply_force(force.x, force.y)

                # keep orientation locked to steering and prevent angular spin
                self.entity.body.angle = self.entity.angle
                self.entity.body.angular_velocity = 0.0

                # sync entity pos to body
                pos = self.entity.body.position
                self.entity.x = float(pos.x)
                self.entity.y = float(pos.y)
            except Exception:
                # fallback: directly set velocity
                self.entity.body.velocity = (self.entity.vx, self.entity.vy)
                self.entity.body.angle = self.entity.angle
                self.entity.body.angular_velocity = 0.0
                self.entity.x = self.entity.body.position.x
                self.entity.y = self.entity.body.position.y