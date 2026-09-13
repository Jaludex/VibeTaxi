from typing import Any
from src.entity.Entity import Entity

class Prop(Entity):
    def __init__(self, x: float, y: float, definition: dict) -> None:
        super().__init__(x, y, definition)
        self.collidable = definition.get("collidable", True)
        self.active = True
        self.alpha = 255
        self.angle = 0
        self._on_collide = definition.get("on_collide")

    def on_collide(self, vehicle: Any) -> None:
        if not self.collidable or self._on_collide is None:
            return
        self._on_collide(self, vehicle)