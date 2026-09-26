from src.states.entity.BaseEntityState import BaseEntityState

class PassengerRideState(BaseEntityState):
    def enter(self, **kwargs):
        self.entity.vx = 0
        self.entity.vy = 0
        self.taxi = kwargs.get("taxi")
        self.entity.change_animation("idle")
        self.entity.time_riding = 0.0
        self.entity.damage_taken = 0.0
        if self.taxi:
            self.entity.initial_taxi_health = self.taxi.health

    def update(self, dt):
        if self.taxi:
            self.entity.x = self.taxi.x
            self.entity.y = self.taxi.y
            if hasattr(self.entity, "initial_taxi_health"):
                self.entity.damage_taken = max(0, self.entity.initial_taxi_health - self.taxi.health)