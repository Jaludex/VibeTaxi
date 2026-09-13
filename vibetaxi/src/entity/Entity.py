import settings

from gale.tilemap import move_and_collide

from src.mixins.DrawableMixin import DrawableMixin
from src.mixins.CollidableMixin import CollidableMixin

class Entity(DrawableMixin, CollidableMixin):
    def __init__(self, x: float, y: float, definition: dict = None) -> None:
        self.x = x
        self.y = y
        self.def_data = definition or {}

        self.texture_id = self.def_data.get("texture", "")
        self.frame_index = self.def_data.get("frame", 0)

        if self.texture_id and self.frame_index is not None:
            frame = settings.FRAMES[self.texture_id][self.frame_index]
            self.height = frame.height
            self.width = frame.width
        else:
            self.height = 0
            self.width = 0
            
        self.vx = 0
        self.vy = 0
        
        self.tilemap = None

    def update(self, dt: float) -> None:
        if self.tilemap is not None:
            tl_x = self.x - self.width / 2
            tl_y = self.y - self.height / 2

            # Movimiento contra la capa buildings
            tl_x, tl_y, hit_wall_x, hit_wall_y = move_and_collide(
                self.tilemap,
                "buildings",
                tl_x,
                tl_y,
                self.width,
                self.height,
                self.vx * dt,
                self.vy * dt,
            )

            self.x = tl_x + self.width / 2
            self.y = tl_y + self.height / 2
            
            if hit_wall_x or hit_wall_y:
                if hasattr(self, "speed"):
                    self.speed *= 0.5
        else:
            self.x += self.vx * dt
            self.y += self.vy * dt
            
        if self.tilemap is not None:
            half_w = self.width / 2
            half_h = self.height / 2
            if self.x - half_w < 0:
                self.x = half_w
            elif self.x + half_w > self.tilemap.pixel_width:
                self.x = self.tilemap.pixel_width - half_w
            if self.y - half_h < 0:
                self.y = half_h
            elif self.y + half_h > self.tilemap.pixel_height:
                self.y = self.tilemap.pixel_height - half_h