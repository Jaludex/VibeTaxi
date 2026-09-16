from gale.state import BaseState

class TrafficCarIdleState(BaseState):
    def __init__(self, entity, sm):
        self.entity = entity
        self.sm = sm

    def enter(self, **kwargs):
        self.entity.speed = 0
        self.entity.vx = 0
        self.entity.vy = 0

    def update(self, dt):
        if self.entity.body is not None:
            self.entity.body.velocity = (0, 0)
            self.entity.body.angular_velocity = 0.0
            pos = self.entity.body.position
            self.entity.x = float(pos.x)
            self.entity.y = float(pos.y)
            self.entity.angle = self.entity.body.angle
