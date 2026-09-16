from gale.state import BaseState

class TrafficCarCrashedState(BaseState):
    def __init__(self, entity, sm):
        self.entity = entity
        self.sm = sm

    def enter(self, **kwargs):
        self.entity.speed = 0
        if self.entity.body is not None:
            try:
                self.entity.body.set_damping(3.0, 3.0)
            except Exception:
                pass

    def update(self, dt):
        if self.entity.body is not None:
            pos = self.entity.body.position
            self.entity.x = float(pos.x)
            self.entity.y = float(pos.y)
            self.entity.angle = self.entity.body.angle

    def exit(self):
        pass

    def on_input(self, input_id, input_data):
        pass
