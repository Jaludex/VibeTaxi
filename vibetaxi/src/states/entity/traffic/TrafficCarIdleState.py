from gale.state import BaseState

class TrafficCarIdleState(BaseState):
    def __init__(self, entity, sm):
        self.entity = entity
        self.sm = sm

    def enter(self, **kwargs):
        self.entity.free_physics = True
        self.entity.speed = 0
        self.entity.vx = 0
        self.entity.vy = 0
        self.entity.is_accelerating = False
        self.entity.is_braking = True
        if self.entity.body is not None:
            try:
                self.entity.body.velocity = (0, 0)
                self.entity.body.angular_velocity = 0.0
                self.entity.body.set_damping(4.0, 6.0)
                pm_body = getattr(self.entity.body, '_pm_body', None)
                if pm_body is not None:
                    for s in pm_body.shapes:
                        s.friction = 1.5
            except Exception:
                pass

    def update(self, dt):
        pass

    def exit(self):
        self.entity.free_physics = False

    def on_input(self, input_id, input_data):
        pass
