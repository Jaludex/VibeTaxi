from src.states.entity.BaseEntityState import BaseEntityState

class PassengerRideState(BaseEntityState):
    def enter(self, **kwargs):
        self.entity.vx = 0
        self.entity.vy = 0
        self.taxi = kwargs.get("taxi")
        self.entity.change_animation("idle")

    def update(self, dt):
        if self.taxi:
            self.entity.x = self.taxi.x
            self.entity.y = self.taxi.y