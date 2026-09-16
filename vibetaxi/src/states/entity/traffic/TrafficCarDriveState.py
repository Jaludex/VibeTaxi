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

        # Call the parent update which handles the physics, steering, etc.
        super().update(dt)
        
    def exit(self):
        pass
        
    def on_input(self, input_id, input_data):
        pass
