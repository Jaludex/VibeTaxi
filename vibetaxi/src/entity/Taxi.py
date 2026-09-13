from gale.state import StateMachine

from typing import Any

from src.entity.Car import Car
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

    def update(self, dt):
        self.state_machine.update(dt)
        super().update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if self.state_machine.current:
            self.state_machine.current.on_input(input_id, input_data)