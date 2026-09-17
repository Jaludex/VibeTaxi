import pygame
import math
import random
from typing import Any, List

from gale.physics import BodyType, BoxShape, World
from gale.tilemap import load_tiled_map

import settings

from src.entity.Prop import Prop
from src.entity.Passenger import Passenger
from src.definitions.props import PROPS_DEF
from src.definitions.passengers import PASSENGER_DEFS
from src.entity.Traffic import TrafficSystem


class CityMap:
    def __init__(self, map_key: str = "city") -> None:
        self.tilemap = load_tiled_map(settings.TILEMAPS[map_key])
        self.physics_world = World(gravity=(0, 0))
        self.physics_world._entity_registry = []
        # Register collision callback so physics drives game collision logic
        self.physics_world.on_collision_begin(self._on_collision_begin)

        self.props: List[Prop] = []
        self.particle_emitters: List[Any] = []
        self._load_collisions()
        self._load_props()
        self._load_nodes()
        self.traffic_system = TrafficSystem(self)

    def _load_collisions(self) -> None:
        for obj in self.tilemap.object_layers.get("collisions", []):
            width = getattr(obj, "width", 0)
            height = getattr(obj, "height", 0)
            if width <= 0 or height <= 0:
                continue

            # Tiled's object y is the top edge; center is y - height/2 (same convention as props)
            # Tiled object coordinates are top-left; convert to center for the Body
            body = self.physics_world.create_static_body(
                obj.x + width / 2,
                obj.y + height / 2,
                BoxShape(width=width, height=height, friction=1.0),
            )
            body.user_data = {"kind": "collision", "object": obj}

    def _on_collision_begin(self, body_a, body_b):
        # body.user_data is set to the owning entity in Entity.set_physics
        a = getattr(body_a, 'user_data', None)
        b = getattr(body_b, 'user_data', None)

        try:
            from src.entity.Prop import Prop
            from src.entity.Car import Car
        except Exception:
            Prop = None
            Car = None

        def play_crash_sound(sound_key, base_volume=0.5):
            if getattr(self, 'muted', False):
                return
            try:
                import settings
                sound = settings.SOUNDS.get(sound_key)
                if sound:
                    vol = base_volume * random.uniform(0.8, 1.2)
                    sound.set_volume(max(0.0, min(1.0, vol)))
                    sound.play()
            except Exception:
                pass

        # Helper to increase friction on a body temporarily
        def increase_friction(gale_body, friction=2.0, linear_damping=3.0):
            try:
                pm_body = getattr(gale_body, '_pm_body', None)
                if pm_body is not None:
                    for s in pm_body.shapes:
                        try:
                            s.friction = friction
                        except Exception:
                            pass
                try:
                    gale_body.set_damping(linear_damping, 0.5)
                except Exception:
                    pass
            except Exception:
                pass

        # If a is a Prop and b is a Car-like, notify prop and penalize vehicle speed
        if Prop is not None and Car is not None:
            if isinstance(a, Prop) and (isinstance(b, Car) or hasattr(b, 'speed')):
                # Increase friction/damping so prop doesn't fly
                if getattr(a, 'body', None) is not None:
                    increase_friction(a.body, friction=2.0, linear_damping=3.0)
                # Penalize vehicle speed
                try:
                    if hasattr(b, 'speed'):
                        b.speed *= 0.5
                except Exception:
                    pass
                a.on_collide(b)
                if type(b).__name__ == "Taxi":
                    play_crash_sound("crash_solid", 0.2)
                else:
                    play_crash_sound("crash_solid", 0.06)
            elif isinstance(b, Prop) and (isinstance(a, Car) or hasattr(a, 'speed')):
                if getattr(b, 'body', None) is not None:
                    increase_friction(b.body, friction=2.0, linear_damping=3.0)
                try:
                    if hasattr(a, 'speed'):
                        a.speed *= 0.5
                except Exception:
                    pass
                b.on_collide(a)
                if type(a).__name__ == "Taxi":
                    play_crash_sound("crash_solid", 0.2)
                else:
                    play_crash_sound("crash_solid", 0.06)
        else:
            # Fallback: if user_data types not mapped but entity-like
            if hasattr(a, 'on_collide') and hasattr(b, 'speed'):
                try:
                    b.speed *= 0.5
                except Exception:
                    pass
                try:
                    a.on_collide(b)
                except Exception:
                    pass
                if type(b).__name__ == "Taxi":
                    play_crash_sound("crash_solid", 0.2)
                else:
                    play_crash_sound("crash_solid", 0.06)
            elif hasattr(b, 'on_collide') and hasattr(a, 'speed'):
                try:
                    a.speed *= 0.5
                except Exception:
                    pass
                try:
                    b.on_collide(a)
                except Exception:
                    pass
                if type(a).__name__ == "Taxi":
                    play_crash_sound("crash_solid", 0.2)
                else:
                    play_crash_sound("crash_solid", 0.06)

        # Check car collisions with static obstacles or other cars
        try:
            from src.ParticleEmitter import ParticleEmitter
            is_a_car = Car is not None and (isinstance(a, Car) or hasattr(a, 'speed'))
            is_b_car = Car is not None and (isinstance(b, Car) or hasattr(b, 'speed'))
            is_a_static = isinstance(a, dict) and a.get("kind") == "collision"
            is_b_static = isinstance(b, dict) and b.get("kind") == "collision"

            if is_a_car and is_b_car:
                impact_x = (a.x + b.x) / 2
                impact_y = (a.y + b.y) / 2
                a.speed *= 0.5
                b.speed *= 0.5
                self.add_particle_emitter(ParticleEmitter.create_sparks(impact_x, impact_y))
                if hasattr(a, 'on_collide'): a.on_collide(b)
                if hasattr(b, 'on_collide'): b.on_collide(a)
                
                is_a_taxi = type(a).__name__ == "Taxi"
                is_b_taxi = type(b).__name__ == "Taxi"
                
                if is_a_taxi or is_b_taxi:
                    play_crash_sound("crash_car", 0.3)
                else:
                    play_crash_sound("crash_car", 0.09)
                    
                if is_a_taxi: a.damage(10)
                if is_b_taxi: b.damage(10)

            elif is_a_car and is_b_static:
                if abs(getattr(a, 'speed', 0)) > 20:
                    self.add_particle_emitter(ParticleEmitter.create_sparks(a.x, a.y))
                    if type(a).__name__ == "Taxi":
                        play_crash_sound("crash_wall", 0.3)
                        a.damage(15)
                    else:
                        play_crash_sound("crash_wall", 0.09)
                if hasattr(a, 'on_collide'): a.on_collide(b)
            elif is_b_car and is_a_static:
                if abs(getattr(b, 'speed', 0)) > 20:
                    self.add_particle_emitter(ParticleEmitter.create_sparks(b.x, b.y))
                    if type(b).__name__ == "Taxi":
                        play_crash_sound("crash_wall", 0.3)
                        b.damage(15)
                    else:
                        play_crash_sound("crash_wall", 0.09)
                if hasattr(b, 'on_collide'): b.on_collide(a)
        except Exception:
            pass

    def add_particle_emitter(self, emitter) -> None:
        self.particle_emitters.append(emitter)

    def _load_nodes(self) -> None:
        self.nodes = {}
        for obj in self.tilemap.object_layers.get("nodes", []):
            center_x = obj.x + obj.width / 2
            center_y = obj.y + obj.height / 2
            
            node_name = obj.name if obj.name and obj.name not in self.nodes.keys() else f"node_{len(self.nodes)}"
            self.nodes[node_name] = (center_x, center_y)

    def _load_props(self) -> None:
        for obj in self.tilemap.object_layers.get("props", []):
            tile_index = obj.properties.get("tile_index")

            if tile_index in PROPS_DEF:
                definition = PROPS_DEF[tile_index]
                center_x = obj.x + obj.width / 2
                center_y = obj.y - obj.height / 2

                prop = Prop(center_x, center_y, definition)
                # Make props dynamic so they can be pushed by vehicles/bodies
                from gale.physics import BoxShape as GPBoxShape
                shape = GPBoxShape(width=prop.width, height=prop.height, friction=0.9)
                prop.set_physics(
                    self.physics_world,
                    body_type=BodyType.DYNAMIC,
                    shape=shape,
                )
                # Give props moderate damping so they don't drift forever
                if prop.body is not None:
                    try:
                        prop.body.set_damping(1.5, 0.5)
                    except Exception:
                        pass

                self.props.append(prop)

    def get_taxi_spawn_position(self, default: tuple = (400, 300)) -> tuple:
        spawner_layer = self.tilemap.object_layers.get("taxi-spawns", [])
        if spawner_layer:
            obj = spawner_layer[0]
            center_x = obj.x + getattr(obj, "width", 0) / 2
            center_y = obj.y + getattr(obj, "height", 0) / 2
            return (center_x, center_y)
        return default

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.tilemap.pixel_width, self.tilemap.pixel_height)

    def fixed_update(self) -> None:
        self.physics_world.fixed_update()
        for entity in getattr(self.physics_world, "_entity_registry", []):
            entity.sync_body_to_entity()

    def update(self, dt: float, camera: Any = None) -> None:
        for prop in self.props:
            if hasattr(prop, 'update'):
                prop.update(dt)
        for emitter in self.particle_emitters:
            emitter.update(dt)
        self.particle_emitters = [e for e in self.particle_emitters if not e.is_finished()]
        self.traffic_system.update(dt, camera)


    def render_debug(self, surface, camera=None):
        import pygame
        if not getattr(__import__('settings'), 'PHYSICS_DEBUG', False):
            return

        # Draw collision rects for bodies registered in the physics world
        for entity in getattr(self.physics_world, '_entity_registry', []):
            if getattr(entity, 'active', True) is False:
                continue
            try:
                # Prefer oriented polygon when available
                if hasattr(entity, 'get_collision_polygon'):
                    poly = entity.get_collision_polygon()
                    if camera is not None:
                        poly = [camera.apply(pygame.Rect(x, y, 0, 0)).topleft for x, y in poly]
                        # camera.apply returns a rect, top-left is position
                        poly = [(p[0], p[1]) for p in poly]
                    pygame.draw.polygon(surface, (255, 0, 0), poly, width=1)
                else:
                    rect = entity.get_collision_rect()
                    if camera is not None:
                        rect = camera.apply(rect)
                    pygame.draw.rect(surface, (255, 0, 0), rect, width=1)

                # draw center
                cx, cy = int(entity.x), int(entity.y)
                if camera is not None:
                    tmp = camera.apply(pygame.Rect(cx, cy, 0, 0))
                    cx, cy = tmp.x, tmp.y
                pygame.draw.circle(surface, (0, 255, 0), (cx, cy), 2)
            except Exception:
                pass

        # Also draw the raw collision objects from the Tiled layer for reference
        try:
            coll_objs = self.tilemap.object_layers.get('collisions', [])
            for obj in coll_objs:
                try:
                    ox = obj.x
                    oy = obj.y
                    ow = getattr(obj, 'width', 0)
                    oh = getattr(obj, 'height', 0)
                    if ow <= 0 or oh <= 0:
                        continue

                    rect = pygame.Rect(ox, oy, ow, oh)
                    if camera is not None:
                        rect = camera.apply(rect)
                        # camera.apply returns a rect
                    # semi-transparent fill
                    try:
                        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                        s.fill((255, 0, 0, 40))
                        surface.blit(s, (rect.x, rect.y))
                    except Exception:
                        # fallback: draw light border
                        pass

                    pygame.draw.rect(surface, (255, 100, 100), rect, width=1)
                except Exception:
                    pass

            # Draw node objects (spawn/waypoints) with their names
            nodes = self.tilemap.object_layers.get('nodes', [])
            font = getattr(__import__('settings'), 'FONTS', {}).get('minecraft')
            for obj in nodes:
                try:
                    ox = obj.x
                    oy = obj.y
                    ow = getattr(obj, 'width', 0)
                    oh = getattr(obj, 'height', 0)
                    if ow <= 0 or oh <= 0:
                        # draw small rect centered on point
                        ow = oh = 16
                        ox = ox - ow/2
                        oy = oy - oh/2

                    rect = pygame.Rect(ox, oy, ow, oh)
                    if camera is not None:
                        rect = camera.apply(rect)

                    # fill and border
                    try:
                        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                        s.fill((0, 0, 255, 40))
                        surface.blit(s, (rect.x, rect.y))
                    except Exception:
                        pass
                    pygame.draw.rect(surface, (0, 120, 255), rect, width=1)

                    # draw name
                    name = getattr(obj, 'name', None) or ''
                    if name and font is not None:
                        text_surf = font.render(name, False, (255, 255, 255))
                        tx = rect.x + rect.width/2 - text_surf.get_width()/2
                        ty = rect.y - text_surf.get_height() - 2
                        surface.blit(text_surf, (tx, ty))
                except Exception:
                    pass
        except Exception:
            pass

    def render_layers(self, surface: pygame.Surface, camera: Any = None, layer_names: list = None) -> None:
        target_layers = layer_names or []
        for name in target_layers:
            self._render_single_layer(surface, camera, name)
            

    def _render_single_layer(self, surface: pygame.Surface, camera: Any, name: str) -> None:
        grid = self.tilemap.get_layer(name)
        row_range, col_range = (
            range(self.tilemap.rows), range(self.tilemap.cols)
        ) if camera is None else self.tilemap._visible_range(camera)

        for row in row_range:
            for col in col_range:
                gid = grid[row][col]
                if gid == 0:
                    continue
                tileset = self.tilemap.tileset_for_gid(gid)
                if tileset is None:
                    continue
                source_rect = tileset.rect_for(gid)
                x, y = self.tilemap.position_of(row, col)

                if camera is None:
                    surface.blit(tileset.image, (x, y), source_rect)
                else:
                    dest_rect = camera.apply(
                        pygame.Rect(x, y, self.tilemap.tile_width, self.tilemap.tile_height)
                    )
                    surface.blit(tileset.image, dest_rect, source_rect)

    def render_car_silhouette_if_obstructed(self, surface: pygame.Surface, car, camera: Any = None) -> None:
        rect = car.get_collision_rect()
        
        is_covered = False
        min_row = max(0, int(rect.top // self.tilemap.tile_height))
        min_col = max(0, int(rect.left // self.tilemap.tile_width))
        max_row = min(self.tilemap.rows - 1, int((rect.bottom - 1) // self.tilemap.tile_height))
        max_col = min(self.tilemap.cols - 1, int((rect.right - 1) // self.tilemap.tile_width))

        for name in settings.TILED_UPPER_SHADOW_LAYERS:
            if name not in self.tilemap.layer_names():
                continue
            grid = self.tilemap.get_layer(name)
            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    if grid[row][col] != 0:
                        is_covered = True
                        break
                if is_covered:
                    break
            if is_covered:
                break

        if not is_covered:
            return

        texture = settings.TEXTURES[car.texture_id]
        frame = settings.FRAMES[car.texture_id][car.frame_index]
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        image.blit(texture, (0, 0), frame)

        angle = getattr(car, "angle", None)
        if angle is not None:
            angle_offset = getattr(car, "angle_offset", 0)
            degrees = math.degrees(-angle) + angle_offset
            image = pygame.transform.rotate(image, degrees)

        mask = pygame.mask.from_surface(image)
        silhouette = mask.to_surface(setcolor=(0, 0, 0, 160), unsetcolor=(0, 0, 0, 0))

        sil_rect = silhouette.get_rect(center=(car.x, car.y))
        if camera is not None:
            sil_rect = camera.apply(sil_rect)

        surface.blit(silhouette, sil_rect)

    def generate_passengers(self, spawn_chance: float = 0.3) -> List[Passenger]:
        spawned_passengers = []
        node_names = list(self.nodes.keys())
        
        if len(node_names) < 2:
            print("Advertencia: Hay menos de 2 nodos cargados.")
            return []
        
        from src.definitions.passengers import PASSENGER_DEFS

        for name, (x, y) in self.nodes.items():
            if random.random() < spawn_chance:
                possible_destinations = [n for n in node_names if n != name]
                destination_name = random.choice(possible_destinations)
                
                destination_pos = self.nodes[destination_name]
                
                ped_key = random.choice(list(PASSENGER_DEFS.keys()))
                definition = PASSENGER_DEFS[ped_key].copy()
                
                definition["music_preference"] = random.choice(settings.MUSIC_GENRES)
                
                passenger = Passenger(x, y, destination_name, destination_pos, definition)
                spawned_passengers.append(passenger)
                
        return spawned_passengers
    def render_traffic(self, surface: pygame.Surface, camera: Any = None) -> None:
        self.traffic_system.render(surface, camera)
