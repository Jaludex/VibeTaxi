from src.states.entity.BaseEntityState import BaseEntityState
from src import commands

class TaxiIdleState(BaseEntityState):
    def enter(self, **kwargs):
        self.entity.speed = 0
        self.entity.vx = 0
        self.entity.vy = 0

    def update(self, dt):
        is_accelerating = getattr(self.entity, "is_accelerating", False)
        is_braking = getattr(self.entity, "is_braking", False)
        
        if is_accelerating and not is_braking:
            self.state_machine.change('drive')

    def on_input(self, input_id, input_data):
        if input_id == "mouse_click":
            if input_data.pressed:
                commands.ACCELERATE.execute(self.entity)
            else:
                commands.STOP_ACCELERATE.execute(self.entity)
        elif input_id == "brake":
            if input_data.pressed:
                commands.BRAKE.execute(self.entity)
            else:
                commands.STOP_BRAKE.execute(self.entity)