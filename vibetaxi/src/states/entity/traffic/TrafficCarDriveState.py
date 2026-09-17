import math
from src.states.entity.CarDriveState import CarDriveState

class TrafficCarDriveState(CarDriveState):
    def __init__(self, entity, sm):
        super().__init__(entity, sm)
        self.look_ahead_distance = 60.0

    def enter(self, **kwargs):
        self.entity.is_accelerating = True
        self.entity.is_braking = False

    def update(self, dt):
        dx = self.entity.target_x - self.entity.x
        dy = self.entity.target_y - self.entity.y
        distance = math.hypot(dx, dy)
        
        should_brake = False
        if self.entity.traffic_system:
            all_cars = list(self.entity.traffic_system.active_cars)
            taxi = getattr(self.entity.traffic_system.city_map, 'taxi', None)
            if taxi:
                all_cars.append(taxi)
                
            for other in all_cars:
                if other is self.entity:
                    continue
                    
                dist_x = other.x - self.entity.x
                dist_y = other.y - self.entity.y
                dist = math.hypot(dist_x, dist_y)
                
                if dist < 80.0:
                    angle_to_other = math.atan2(dist_y, dist_x)
                    angle_diff = (angle_to_other - self.entity.angle + math.pi) % (2 * math.pi) - math.pi
                    if abs(angle_diff) < math.radians(45):
                        # Check if we are also in their front cone
                        other_angle_to_us = math.atan2(-dist_y, -dist_x)
                        other_angle_diff = (other_angle_to_us - getattr(other, 'angle', 0) + math.pi) % (2 * math.pi) - math.pi
                        
                        if abs(other_angle_diff) < math.radians(45):
                            # Both see each other. Break tie with ID so one yields.
                            if id(self.entity) < id(other):
                                should_brake = True
                                break
                        else:
                            # They don't see us in front of them, so we must yield (we are behind or coming from side)
                            should_brake = True
                            break

        self.entity.is_braking = should_brake
        self.entity.is_accelerating = True
        
        # Check distance to target node
        if distance < 30.0:
            if self.entity.next_node_name and self.entity.traffic_system:
                next_pos = self.entity.traffic_system.get_node_position(self.entity.next_node_name)
                next_next = self.entity.traffic_system.get_node_next(self.entity.next_node_name)
                if next_pos:
                    self.entity.target_x, self.entity.target_y = next_pos
                    self.entity.next_node_name = next_next
                else:
                    self.state_machine.change('idle')
                    return
            else:
                self.state_machine.change('idle')
                return

        # Call the parent update which handles the physics, steering, etc.
        super().update(dt)
        
    def exit(self):
        pass
        
    def on_input(self, input_id, input_data):
        pass
