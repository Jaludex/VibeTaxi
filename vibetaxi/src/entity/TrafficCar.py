import math
from gale.state import StateMachine
from src.entity.Car import Car
from src.states.entity.traffic.TrafficCarDriveState import TrafficCarDriveState
from src.states.entity.traffic.TrafficCarCrashedState import TrafficCarCrashedState

from src.states.entity.traffic.TrafficCarIdleState import TrafficCarIdleState

class TrafficCar(Car):
    def __init__(self, x, y, definition, traffic_system=None):
        super().__init__(x, y, definition)
        self.traffic_system = traffic_system
        self.next_node_name = None
        self.crashed = False

        self.state_machine = StateMachine({
            'idle': lambda sm: TrafficCarIdleState(self, sm),
            'drive': lambda sm: TrafficCarDriveState(self, sm),
            'crashed': lambda sm: TrafficCarCrashedState(self, sm)
        })
        self.state_machine.change('drive')
        
    def set_path(self, target_x, target_y, next_node_name):
        self.target_x = target_x
        self.target_y = target_y
        self.next_node_name = next_node_name
        # point towards target initially
        self.angle = math.atan2(target_y - self.y, target_x - self.x)
        self.speed = self.max_speed * 0.5 # Start with some speed

    def on_collide(self, other):
        # Crash logic only on high speed impacts
        if not self.crashed:
            my_vx = getattr(self, 'vx', 0)
            my_vy = getattr(self, 'vy', 0)
            other_vx = getattr(other, 'vx', 0)
            other_vy = getattr(other, 'vy', 0)
            
            rel_speed = math.hypot(my_vx - other_vx, my_vy - other_vy)
            
            # Check absolute speed too, just in case physics/velocities desync
            my_speed = abs(getattr(self, 'speed', 0))
            other_speed = abs(getattr(other, 'speed', 0))
            
            if rel_speed >= 150 or my_speed >= 150 or other_speed >= 150:
                self.crashed = True
                self.state_machine.change('crashed')

    def update(self, dt):
        self.state_machine.update(dt)
        super().update(dt)

    def on_input(self, input_id, input_data):
        pass
