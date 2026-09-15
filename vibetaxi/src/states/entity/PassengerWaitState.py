from src.states.entity.BaseEntityState import BaseEntityState

class PassengerWaitState(BaseEntityState):
    def enter(self, **kwargs):
        self.entity.vx = 0
        self.entity.vy = 0
        self.entity.target_taxi = None
        self.entity.change_animation("idle")

    def update(self, dt):
        pass