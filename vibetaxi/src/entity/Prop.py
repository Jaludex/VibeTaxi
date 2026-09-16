from typing import Any
from src.entity.Entity import Entity
from gale.timer import Timer

class Prop(Entity):
    def __init__(self, x: float, y: float, definition: dict) -> None:
        super().__init__(x, y, definition)
        # Keep collidable flag for legacy checks, but physics drives collisions
        self.collidable = definition.get("collidable", True)
        self.active = True
        self.alpha = 255
        self.angle = 0
        # removal scheduling guard
        self._removal_scheduled = False

    def on_collide(self, vehicle: Any) -> None:
        # Physics handles the physical response (pushing). On first contact,
        # schedule a one-shot removal after 5 seconds and mark as non-interactive.
        if self._removal_scheduled:
            return

        self._removal_scheduled = True

        # Optionally do a small callback or effect here (sound, particles)
        # Schedule actual removal after 5 seconds
        def remove_prop():
            # mark inactive for rendering and game logic
            self.active = False
            # destroy physics body if present
            try:
                if self.body is not None:
                    self.body.destroy()
                    self.body = None
            except Exception:
                pass

        Timer.after(5.0, remove_prop)
