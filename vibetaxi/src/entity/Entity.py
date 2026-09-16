import settings

from gale.physics import BodyType, BoxShape

from src.mixins.DrawableMixin import DrawableMixin


class Entity(DrawableMixin):
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

        self.collision_width = self.width
        self.collision_height = self.height

        self.vx = 0
        self.vy = 0

        self.tilemap = None
        self.world = None
        self.body = None
        self.physics_enabled = False

    def set_physics(
        self,
        world,
        *,
        body_type: int = BodyType.DYNAMIC,
        shape=None,
        width: float = None,
        height: float = None,
        offset=(0, 0),
        is_sensor: bool = False,
    ):
        if world is None:
            return None

        self.world = world
        self.physics_enabled = True

        if shape is None:
            default_width = width if width is not None else self.width
            default_height = height if height is not None else self.height
            if default_width > 0 and default_height > 0:
                shape = BoxShape(
                    width=default_width,
                    height=default_height,
                    offset=offset,
                    is_sensor=is_sensor,
                )

        if shape is None:
            return None

        if self.body is not None:
            self.body.destroy()

        if body_type == BodyType.STATIC:
            self.body = world.create_static_body(self.x, self.y, shape)
        elif body_type == BodyType.KINEMATIC:
            self.body = world.create_kinematic_body(self.x, self.y, shape)
        else:
            self.body = world.create_dynamic_body(self.x, self.y, shape)

        self.body.user_data = self
        self.body.position = (self.x, self.y)
        self.body.angle = getattr(self, "angle", 0.0)
        self.body.angular_velocity = 0.0

        registry = getattr(world, "_entity_registry", None)
        if registry is not None and self not in registry:
            registry.append(self)

        return self.body

    def sync_body_to_entity(self) -> None:
        if self.body is None:
            return

        pos = self.body.position
        self.x = float(pos.x)
        self.y = float(pos.y)

        if hasattr(self, "angle"):
            # Keep body angle aligned to entity steering but avoid spinning
            self.body.angle = self.angle
            self.body.angular_velocity = 0.0

    def get_collision_rect(self):
        # Axis-aligned bounding box fallback (keeps compatibility)
        import pygame
        c_width = getattr(self, "collision_width", self.width)
        c_height = getattr(self, "collision_height", self.height)
        return pygame.Rect(
            round(self.x - c_width / 2),
            round(self.y - c_height / 2),
            c_width,
            c_height,
        )

    def get_collision_polygon(self):
        # Returns list of 4 points for the oriented collision rectangle using
        # the same center and rotation used for rendering to ensure alignment.
        import pygame
        hw = getattr(self, 'collision_width', self.width) / 2.0
        hh = getattr(self, 'collision_height', self.height) / 2.0

        # corners local coordinates (clockwise)
        corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]

        center_x, center_y, degrees = self.get_render_center_and_degrees()

        poly = []
        for lx, ly in corners:
            v = pygame.math.Vector2(lx, ly)
            # rotate using same sign used for pivot math in Drawable: rotate(-degrees)
            rv = v.rotate(-degrees)
            poly.append((center_x + rv.x, center_y + rv.y))

        return poly

    def get_render_center_and_degrees(self):
        # Returns (center_x, center_y, degrees) matching Drawable.render logic
        import math
        import pygame
        center_x, center_y = self.x, self.y
        angle = getattr(self, 'angle', 0.0)
        angle_offset = getattr(self, 'angle_offset', 0)
        degrees = math.degrees(-angle) + angle_offset

        pivot_x = getattr(self, 'pivot_x', 0)
        pivot_y = getattr(self, 'pivot_y', 0)
        if pivot_x != 0 or pivot_y != 0:
            offset = pygame.math.Vector2(pivot_x, pivot_y)
            # same rotation used in Drawable: rotated_offset = offset.rotate(-degrees)
            rotated_offset = offset.rotate(-degrees)
            center_x = (self.x + pivot_x) - rotated_offset.x
            center_y = (self.y + pivot_y) - rotated_offset.y

        return center_x, center_y, degrees

    def align_body_to_render_center(self):
        # Move the physics body so its position equals the rendered center
        if self.body is None:
            return
        try:
            cx, cy, _ = self.get_render_center_and_degrees()
            self.body.position = (cx, cy)
            # Keep entity coords in sync
            self.x = float(cx)
            self.y = float(cy)
        except Exception:
            pass

    def update(self, dt: float) -> None:
        if self.body is not None:
            self.sync_body_to_entity()
            if hasattr(self, "angle"):
                self.body.angle = self.angle
                self.body.angular_velocity = 0.0
            if hasattr(self, "vx") and hasattr(self, "vy"):
                self.body.velocity = (self.vx, self.vy)
            return

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