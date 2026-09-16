from gale.state import BaseState

class TrafficCarCrashedState(BaseState):
    def __init__(self, entity, sm):
        self.entity = entity
        self.sm = sm

    def enter(self, **kwargs):
        self.entity.free_physics = True
        self.entity.speed = 0
        self.entity.vx = 0
        self.entity.vy = 0
        if self.entity.body is not None:
            try:
                # Amortiguación moderada para que frene gradualmente sin deslizarse eternamente
                self.entity.body.set_damping(3.0, 5.0)
                
                # Fricción para que responda a choques con paredes/otros objetos
                pm_body = getattr(self.entity.body, '_pm_body', None)
                if pm_body is not None:
                    for s in pm_body.shapes:
                        s.friction = 1.2
            except Exception:
                pass

    def update(self, dt):
        # La posición y el ángulo se sincronizan automáticamente desde el cuerpo físico en sync_body_to_entity
        pass

    def exit(self):
        self.entity.free_physics = False

    def on_input(self, input_id, input_data):
        pass

