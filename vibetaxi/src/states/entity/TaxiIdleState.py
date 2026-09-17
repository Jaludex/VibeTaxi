from src.states.entity.BaseEntityState import BaseEntityState
from src import commands

class TaxiIdleState(BaseEntityState):
    def enter(self, **kwargs):
        self.entity.speed = 0
        self.entity.vx = 0
        self.entity.vy = 0

    def update(self, dt):
        is_accelerating = getattr(self.entity, "is_accelerating", False)
        is_reversing = getattr(self.entity, "is_reversing", False)
        is_braking = getattr(self.entity, "is_braking", False)
        
        self.entity.is_drifting = False
        
        if (is_accelerating or is_reversing) and not is_braking:
            self.state_machine.change('drive')