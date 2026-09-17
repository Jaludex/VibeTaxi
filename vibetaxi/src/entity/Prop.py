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

        damage_amount = self.def_data.get("damage", 0)
        if damage_amount > 0 and hasattr(vehicle, 'damage'):
            vehicle.damage(damage_amount)

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
    def update(self, dt: float) -> None:
        super().update(dt)
        if hasattr(self, 'particle_system') and self.particle_system:
            self.particle_system.update(dt)

    def render(self, surface, camera=None):
        # Skip rendering once inactive
        if getattr(self, 'active', True):
            super().render(surface, camera)
            
        if hasattr(self, 'particle_system') and self.particle_system:
            if hasattr(self.particle_system, 'render'):
                try:
                    self.particle_system.render(surface, camera)
                    return
                except TypeError:
                    pass
            if camera:
                import pygame
                for p in self.particle_system.particles:
                    if self.particle_system.timer < p.life_time:
                        rect = camera.apply(pygame.Rect(int(p.x), int(p.y), 4, 4))
                        s = pygame.Surface((4, 4), pygame.SRCALPHA)
                        color = (p.color[0], p.color[1], p.color[2], p.color[3])
                        pygame.draw.circle(s, color, (2, 2), 2)
                        surface.blit(s, rect)
            else:
                self.particle_system.render(surface)
