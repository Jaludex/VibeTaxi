import math
import random
import pygame
import settings
from gale.animation import Animation
from gale.timer import Timer
from src.entity.Entity import Entity
from src.definitions.passengers import PASSENGER_DEFS

# Despawn directions normalized offsets
DESPAWN_DIR_OFFSETS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
    "rigth": (1, 0) # Support common typo in tiled
}

# Static surface cache to eliminate dynamic allocations per frame
_PED_FRAME_CACHE = {}

def _get_ped_surface(texture_id: str, frame_index: int, flipped: bool) -> pygame.Surface:
    key = (texture_id, frame_index, flipped)
    surf = _PED_FRAME_CACHE.get(key)
    if surf is None:
        texture = settings.TEXTURES[texture_id]
        frame = settings.FRAMES[texture_id][frame_index]
        base = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        base.blit(texture, (0, 0), frame)
        if flipped:
            surf = pygame.transform.flip(base, True, False)
        else:
            surf = base
        _PED_FRAME_CACHE[key] = surf
    return surf

class PedestrianNPC(Entity):
    def __init__(self, x: float, y: float, current_node: str, pedestrian_system, definition_key: str = None):
        if not definition_key or definition_key not in PASSENGER_DEFS:
            definition_key = random.choice(list(PASSENGER_DEFS.keys()))
        
        self.def_key = definition_key
        definition = dict(PASSENGER_DEFS[definition_key])
        
        super().__init__(x, y, definition)
        self.pedestrian_system = pedestrian_system
        self.current_node = current_node
        self.previous_node = None
        self.target_node = None
        self.target_x = x
        self.target_y = y
        
        # Blocked node tracking to avoid deadlocks & building cuts
        self.blocked_node = None
        self.blocked_timer = 0.0
        
        # Movement and rendering parameters
        self.move_speed = random.uniform(28.0, 42.0) # Pixels per second
        self.jump_offset_y = 0.0
        self.flipped = False
        self.alpha = 255
        self.angle = 0.0
        
        # State: "walking", "waiting_car", "hit", "down", "getting_up", "despawning", "dead"
        self.state = "walking"
        self.despawn_timer = 0.0
        self.despawn_duration = 0.5
        self.despawn_dir = (0, -1)
        
        # Hit / launch state
        self.hit_timer = 0.0
        self.hit_duration = 0.7 # Flight and tumble through air
        self.hit_vx = 0.0
        self.hit_vy = 0.0
        
        # Ground recovery state (staying down and getting up)
        self.down_timer = 0.0
        self.down_duration = 1.4 # Time lying on the floor
        self.getup_timer = 0.0
        self.getup_duration = 0.5 # Time to smoothly stand back up
        self.getup_start_angle = 0.0
        
        # Waiting for car to pass & deadlock resolution timer
        self.wait_timer = 0.0
        self.total_wait_time = 0.0 # Time accumulated waiting at this location
        self.check_car_timer = random.uniform(0.0, 0.2)
        
        # Walking animation bounce timer
        self.walk_timer = random.uniform(0.0, 1.0)
        self.hop_frequency = 12.0 # Speed of hop
        self.hop_height = 3.5 # Height of small hop
        
        # Setup sprite animations if available in definition
        self.animations = {}
        self.current_animation = None
        if "animations" in definition:
            for anim_id, values in definition["animations"].items():
                self.animations[anim_id] = Animation(
                    values["frames"],
                    values.get("interval", 0.15),
                    loops=values.get("loops")
                )
        
        self.change_animation("walk")
        self._select_next_node()

    def change_animation(self, anim_id: str) -> None:
        new_anim = self.animations.get(anim_id)
        if new_anim and new_anim != self.current_animation:
            self.current_animation = new_anim
            self.current_animation.reset()
            self.frame_index = self.current_animation.get_current_frame()

    def _select_next_node(self) -> None:
        """Picks the next node (prioritizing moving forward over backtracking) or begins despawning."""
        node_info = self.pedestrian_system.get_npc_node(self.current_node)
        if not node_info:
            self.state = "dead"
            return
            
        is_despawn = node_info.get("despawn", False)
        raw_next = node_info.get("next", [])
        # Deduplicate next_nodes preserving order and exclude current node
        next_nodes = [n for n in list(dict.fromkeys(raw_next)) if n != self.current_node]
        
        # If this node can despawn, check probability
        if is_despawn:
            # If there are no next nodes, it must despawn
            if not next_nodes or random.random() < 0.45:
                dir_name = node_info.get("dir_despawn", "up").lower()
                self.start_despawn(dir_name)
                return
                
        if not next_nodes:
            self.start_despawn(node_info.get("dir_despawn", "up").lower())
            return
            
        # Avoid recently blocked node if other options exist
        if self.blocked_timer > 0 and self.blocked_node in next_nodes:
            filtered_nodes = [n for n in next_nodes if n != self.blocked_node]
            if filtered_nodes:
                next_nodes = filtered_nodes
            else:
                # All available routes from here are blocked: despawn cleanly
                self.start_despawn(node_info.get("dir_despawn", "up").lower())
                return

        # Weighted choice: make returning to previous_node much less likely
        forward_nodes = [n for n in next_nodes if n != self.previous_node]
        if forward_nodes:
            # 85% chance to pick forward nodes, only 15% chance to backtrack if previous is valid
            if self.previous_node in next_nodes and random.random() < 0.15:
                self.target_node = self.previous_node
            else:
                self.target_node = random.choice(forward_nodes)
        elif self.previous_node in next_nodes:
            self.target_node = self.previous_node
        elif next_nodes:
            self.target_node = random.choice(next_nodes)
        else:
            self.start_despawn("up")
            return
            
        pos = self.pedestrian_system.get_node_pos(self.target_node)
        if pos:
            self.target_x, self.target_y = pos
        else:
            self.state = "dead"
            return
            
        self.total_wait_time = 0.0

    def _recover_from_hit(self) -> None:
        """Finds a safe recovery node with unobstructed line-of-sight after being hit."""
        self.angle = 0.0
        self.jump_offset_y = 0.0
        
        # Verify landing position is not overlapping any building and resolve if needed
        nearby_cols = self.pedestrian_system.get_nearby_collision_rects(self.x, self.y, radius=32.0)
        npc_box = pygame.Rect(int(self.x - 7), int(self.y - 7), 14, 14)
        for r in nearby_cols:
            if r.colliderect(npc_box):
                overlap_left = npc_box.right - r.left
                overlap_right = r.right - npc_box.left
                overlap_top = npc_box.bottom - r.top
                overlap_bottom = r.bottom - npc_box.top
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                if min_overlap == overlap_left:
                    self.x = r.left - 7.5
                elif min_overlap == overlap_right:
                    self.x = r.right + 7.5
                elif min_overlap == overlap_top:
                    self.y = r.top - 7.5
                else:
                    self.y = r.bottom + 7.5
                npc_box.center = (int(self.x), int(self.y))

        # Find nearest walkable node that has direct line-of-sight (no building in between)
        safe_node = self.pedestrian_system.find_nearest_walkable_node(self.x, self.y, max_dist=350.0)
        if safe_node:
            self.current_node = safe_node
            self.target_node = safe_node
            pos = self.pedestrian_system.get_node_pos(safe_node)
            if pos:
                self.target_x, self.target_y = pos
            self.previous_node = None
            self.blocked_node = None
            self.blocked_timer = 0.0
            self.state = "walking"
            self.change_animation("walk")
        else:
            # Trapped with no clear line-of-sight to any node: despawn cleanly without cutting buildings
            self.start_despawn("up")

    def start_despawn(self, dir_name: str) -> None:
        self.state = "despawning"
        self.despawn_timer = 0.0
        self.despawn_dir = DESPAWN_DIR_OFFSETS.get(dir_name, (0, -1))
        self.change_animation("walk")

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 7, self.y - 7, 14, 14)

    def on_hit_by_car(self, car_x: float, car_y: float, car_speed: float = 50.0) -> None:
        """Called when a car (taxi or traffic car) collides with this NPC."""
        if self.state in ("hit", "down", "getting_up", "dead"):
            return
            
        self.state = "hit"
        self.hit_timer = 0.0
        self.change_animation("idle")
        
        # Calculate knockback vector away from car
        dx = self.x - car_x
        dy = self.y - car_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
            dist = math.hypot(dx, dy)
            
        # Normalize and apply knockback impulse
        norm_x = dx / dist
        norm_y = dy / dist
        
        # Speed proportional to car impact
        launch_speed = max(90.0, min(220.0, abs(car_speed) * 1.5))
        self.hit_vx = norm_x * launch_speed
        self.hit_vy = norm_y * launch_speed

    def _check_car_hazard(self) -> None:
        """Checks if there is a car blocking the straight line path in front."""
        all_cars = self.pedestrian_system.get_nearby_cars(self.x, self.y, radius=70.0)
        if not all_cars:
            return
            
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist_sq = dx * dx + dy * dy
        if dist_sq == 0:
            return
        path_dist = math.sqrt(dist_sq)
        dir_x = dx / path_dist
        dir_y = dy / path_dist
        
        # Straight line of sight segment ahead of the pedestrian (strictly in front)
        lookahead = min(path_dist, 48.0)
        p1 = (self.x, self.y)
        p2 = (self.x + dir_x * lookahead, self.y + dir_y * lookahead)
        
        has_car_in_path = False
        
        for car in all_cars:
            car_rect = car.get_collision_rect()
            # 1. Exact straight line-segment intersection with car bounding box
            if car_rect.inflate(8, 8).clipline(p1, p2):
                has_car_in_path = True
                break
                
            # 2. Straight beam corridor projection (forward in [0, lookahead], lateral <= 14px)
            c_dx = car.x - self.x
            c_dy = car.y - self.y
            forward = c_dx * dir_x + c_dy * dir_y
            if 0.0 < forward <= lookahead:
                lateral = abs(-c_dx * dir_y + c_dy * dir_x)
                if lateral <= 14.0:
                    has_car_in_path = True
                    break
                
        if has_car_in_path:
            # Stop and wait for car to pass or clear
            self.state = "waiting_car"
            self.wait_timer = 0.3
            self.change_animation("idle")

    def update(self, dt: float, is_on_screen: bool = True) -> None:
        if self.state == "dead":
            return
            
        if self.blocked_timer > 0:
            self.blocked_timer = max(0.0, self.blocked_timer - dt)
            
        # Update sprite frame animation only if visible on screen
        if is_on_screen and self.current_animation:
            self.current_animation.update(dt)
            self.frame_index = self.current_animation.get_current_frame()
            
        if self.state == "walking":
            if is_on_screen:
                self.walk_timer += dt
                self.jump_offset_y = -abs(math.sin(self.walk_timer * self.hop_frequency)) * self.hop_height
                
                # Periodically check for cars in front
                self.check_car_timer -= dt
                if self.check_car_timer <= 0:
                    self.check_car_timer = 0.15
                    self._check_car_hazard()
                    if self.state != "walking":
                        return
            else:
                self.jump_offset_y = 0.0
            
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist_sq = dx * dx + dy * dy
            
            if dx != 0:
                self.flipped = dx < 0
                
            step = self.move_speed * dt
            if dist_sq <= (step * step) or dist_sq < 16.0:
                self.x = self.target_x
                self.y = self.target_y
                self.previous_node = self.current_node
                self.current_node = self.target_node
                self._select_next_node()
            else:
                dist = math.sqrt(dist_sq)
                self.x += (dx / dist) * step
                self.y += (dy / dist) * step
                
        elif self.state == "waiting_car":
            self.wait_timer -= dt
            self.total_wait_time += dt
            self.jump_offset_y = 0.0
            
            # If waited for >= 4 seconds due to traffic jams / dumb car AI, safely reverse
            if self.total_wait_time >= 4.0:
                self.total_wait_time = 0.0
                blocked_dest = self.target_node
                self.blocked_node = blocked_dest
                self.blocked_timer = 8.0 # avoid this blocked path for 8 seconds
                
                # Safely return to current_node along the known clear path we just came from
                self.target_node = self.current_node
                self.previous_node = blocked_dest
                pos = self.pedestrian_system.get_node_pos(self.target_node)
                if pos:
                    self.target_x, self.target_y = pos
                self.state = "walking"
                self.change_animation("walk")
                return

            if self.wait_timer <= 0:
                self.state = "walking"
                self.change_animation("walk")
                if is_on_screen:
                    self._check_car_hazard()
                
        elif self.state == "hit":
            self.hit_timer += dt
            progress = min(1.0, self.hit_timer / self.hit_duration)
            decay = max(0.0, 1.0 - progress)
            
            step_dx = self.hit_vx * decay * dt
            step_dy = self.hit_vy * decay * dt
            
            # Query nearby collision rects from spatial grid
            nearby_cols = self.pedestrian_system.get_nearby_collision_rects(self.x, self.y, radius=48.0)
            
            # Step X with clamping against nearby buildings
            if step_dx != 0:
                new_x = self.x + step_dx
                test_rect_x = pygame.Rect(int(new_x - 7), int(self.y - 7), 14, 14)
                for r in nearby_cols:
                    if r.colliderect(test_rect_x):
                        self.hit_vx = -self.hit_vx * 0.3
                        if step_dx > 0:
                            new_x = r.left - 7.5
                        else:
                            new_x = r.right + 7.5
                        break
                self.x = new_x

            # Step Y with clamping against nearby buildings
            if step_dy != 0:
                new_y = self.y + step_dy
                test_rect_y = pygame.Rect(int(self.x - 7), int(new_y - 7), 14, 14)
                for r in nearby_cols:
                    if r.colliderect(test_rect_y):
                        self.hit_vy = -self.hit_vy * 0.3
                        if step_dy > 0:
                            new_y = r.top - 7.5
                        else:
                            new_y = r.bottom + 7.5
                        break
                self.y = new_y
                
            # Separation push-out: if overlapping any building, resolve out along shortest penetration axis
            npc_box = pygame.Rect(int(self.x - 7), int(self.y - 7), 14, 14)
            for r in nearby_cols:
                if r.colliderect(npc_box):
                    overlap_left = npc_box.right - r.left
                    overlap_right = r.right - npc_box.left
                    overlap_top = npc_box.bottom - r.top
                    overlap_bottom = r.bottom - npc_box.top
                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                    if min_overlap == overlap_left:
                        self.x = r.left - 7.5
                    elif min_overlap == overlap_right:
                        self.x = r.right + 7.5
                    elif min_overlap == overlap_top:
                        self.y = r.top - 7.5
                    else:
                        self.y = r.bottom + 7.5
                    npc_box.center = (int(self.x), int(self.y))
            
            # Arching bounce and spin while falling
            self.jump_offset_y = -math.sin(progress * math.pi) * 16.0
            self.angle = math.radians(math.sin(progress * math.pi * 2.5) * 65.0)
            
            # When tumble finishes, land flat on the ground
            if self.hit_timer >= self.hit_duration:
                self.state = "down"
                self.down_timer = 0.0
                self.down_duration = random.uniform(1.2, 1.8) # Stay down on ground for a bit
                self.jump_offset_y = 0.0
                self.angle = math.radians(85.0 if self.hit_vx >= 0 else -85.0)
                self.change_animation("idle")

        elif self.state == "down":
            self.down_timer += dt
            self.jump_offset_y = 0.0
            # Small comical dazed twitch on the ground
            twitch = math.sin(self.down_timer * 10.0) * 0.06
            base_angle = math.radians(85.0 if self.hit_vx >= 0 else -85.0)
            self.angle = base_angle + twitch
            
            if self.down_timer >= self.down_duration:
                self.state = "getting_up"
                self.getup_timer = 0.0
                self.getup_duration = 0.5
                self.getup_start_angle = self.angle

        elif self.state == "getting_up":
            self.getup_timer += dt
            t = min(1.0, self.getup_timer / self.getup_duration)
            # Smooth cubic ease rotation back upright
            ease_t = 1.0 - ((1.0 - t) ** 3)
            self.angle = self.getup_start_angle * (1.0 - ease_t)
            # Push off the ground with a small hop to feet
            self.jump_offset_y = -math.sin(t * math.pi) * 4.0
            
            if t >= 1.0:
                self._recover_from_hit()
            
        elif self.state == "despawning":
            self.despawn_timer += dt
            progress = min(1.0, self.despawn_timer / self.despawn_duration)
            
            self.alpha = int(255 * (1.0 - progress))
            
            drift_speed = 20.0
            self.x += self.despawn_dir[0] * drift_speed * dt
            self.y += self.despawn_dir[1] * drift_speed * dt
            
            if is_on_screen:
                self.walk_timer += dt
                self.jump_offset_y = -abs(math.sin(self.walk_timer * self.hop_frequency)) * self.hop_height
            else:
                self.jump_offset_y = 0.0
            
            if progress >= 1.0:
                self.state = "dead"

    def render(self, surface: pygame.Surface, camera=None) -> None:
        if self.state == "dead" or self.alpha <= 0:
            return
            
        render_x = self.x
        render_y = self.y + self.jump_offset_y
        
        image = _get_ped_surface(self.texture_id, self.frame_index, self.flipped)
        
        if self.angle != 0.0:
            angle_offset = getattr(self, "angle_offset", 0)
            degrees = math.degrees(-self.angle) + angle_offset
            image = pygame.transform.rotate(image, degrees)
            
        if self.alpha < 255:
            try:
                tmp = image.copy()
                tmp.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
                image = tmp
            except Exception:
                image.set_alpha(self.alpha)
                
        rect = image.get_rect(center=(int(render_x), int(render_y)))
        if camera is not None:
            rect = camera.apply(rect)
            
        surface.blit(image, rect)
