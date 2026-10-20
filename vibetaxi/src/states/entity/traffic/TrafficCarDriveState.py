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
        dist_to_target_sq = dx * dx + dy * dy
        
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
                dist_sq = dist_x * dist_x + dist_y * dist_y
                
                # Check within 80px (80^2 = 6400)
                if dist_sq < 6400.0:
                    angle_to_other = math.atan2(dist_y, dist_x)
                    angle_diff = (angle_to_other - self.entity.angle + math.pi) % (2 * math.pi) - math.pi
                    if abs(angle_diff) < 0.7853981633974483:  # math.radians(45)
                        # Check if we are also in their front cone
                        other_angle_to_us = math.atan2(-dist_y, -dist_x)
                        other_angle_diff = (other_angle_to_us - getattr(other, 'angle', 0) + math.pi) % (2 * math.pi) - math.pi
                        
                        if abs(other_angle_diff) < 0.7853981633974483:
                            # Both see each other. Break tie with ID so one yields.
                            if id(self.entity) < id(other):
                                should_brake = True
                                break
                        else:
                            # They don't see us in front of them, so we must yield (we are behind or coming from side)
                            should_brake = True
                            break

            # Check for pedestrian NPCs in the car's lane ahead
            if not should_brake and hasattr(self.entity.traffic_system.city_map, "pedestrian_system"):
                p_sys = self.entity.traffic_system.city_map.pedestrian_system
                if p_sys and p_sys.active_npcs:
                    car_cos = math.cos(self.entity.angle)
                    car_sin = math.sin(self.entity.angle)
                    for npc in p_sys.active_npcs:
                        if npc.state == "dead":
                            continue
                        p_dx = npc.x - self.entity.x
                        p_dy = npc.y - self.entity.y
                        if abs(p_dx) > 75 or abs(p_dy) > 75:
                            continue
                        
                        forward = p_dx * car_cos + p_dy * car_sin
                        if -5.0 < forward < 60.0:
                            lateral = abs(-p_dx * car_sin + p_dy * car_cos)
                            if lateral < 22.0:
                                should_brake = True
                                break

        self.entity.is_braking = should_brake
        # Keep is_accelerating = True so CarDriveState does not permanently freeze the car into idle when stopped
        self.entity.is_accelerating = True
        
        # Check distance to target node (30^2 = 900)
        if dist_to_target_sq < 900.0:
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
