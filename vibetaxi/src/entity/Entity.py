import settings

from src.mixins.DrawableMixin import DrawableMixin

class Entity(DrawableMixin):
    def __init__(self, x: float, y: float, definition: dict = None) -> None:
        self.x = x
        self.y = y

        self.texture_id = definition["texture"]
        self.frame_index = definition["frame"]

        frame = settings.FRAMES[self.texture_id][self.frame_index]

        self.height = frame.height
        self.width = frame.width

        self.def_data = definition or {}
        
        self.vx = 0
        self.vy = 0

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt