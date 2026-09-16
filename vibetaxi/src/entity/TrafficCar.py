import math
from gale.state import StateMachine
from src.entity.Car import Car
from src.states.entity.traffic.TrafficCarDriveState import TrafficCarDriveState
from src.states.entity.traffic.TrafficCarCrashedState import TrafficCarCrashedState

class TrafficCar(Car):
    def __init__(self, x, y, definition, traffic_system=None):
        super().__init__(x, y, definition)
        self.traffic_system = traffic_system
        self.next_node_name = None
        self.crashed = False

        self.state_machine = StateMachine({
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
        # Crash logic
        if not self.crashed:
            self.crashed = True
            self.state_machine.change('crashed')

    def update(self, dt):
        self.state_machine.update(dt)
        super().update(dt)

    def on_input(self, input_id, input_data):
        pass
