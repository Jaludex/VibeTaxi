from src.entity.Car import Car
from gale.state import StateMachine
from src.states.entity.TaxiIdleState import TaxiIdleState
from src.states.entity.TaxiDriveState import TaxiDriveState

class Taxi(Car):
    def __init__(self, x, y, definition):
        super().__init__(x, y, definition) 
        
        self.is_accelerating = False
        
        self.state_machine = StateMachine({
            'idle': lambda sm: TaxiIdleState(self, sm),
            'drive': lambda sm: TaxiDriveState(self, sm)
        })
        self.state_machine.change('idle')