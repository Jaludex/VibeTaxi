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
        # per-prop on_collide callback from definitions
        self._on_collide_def = definition.get("on_collide")

    def on_collide(self, vehicle: Any) -> None:
        # Called from physics contact callback. Run per-prop definition callback
        # (if present). The definition is responsible for scheduling any
        # tween/Timer that fades and sets active = False and destroys the body.
        if self._removal_scheduled:
            return

        # If a custom on_collide function is provided in the definitions, call it now
        try:
            if self._on_collide_def is not None:
                # Allow the definition to run an effect (e.g., rotate & fade)
                self._on_collide_def(self, vehicle)
        except Exception:
            # Swallow definition errors to avoid breaking physics loop
            pass

        # mark scheduled so on_collide is idempotent
        self._removal_scheduled = True

        # After the definition possibly changes pivot/visual center, align the physics body
        try:
            self.align_body_to_render_center()
        except Exception:
            pass
    def render(self, surface, camera=None):
        # Skip rendering once inactive
        if not getattr(self, 'active', True):
            return
        super().render(surface, camera)
