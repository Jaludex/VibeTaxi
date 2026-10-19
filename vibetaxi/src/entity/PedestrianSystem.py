import random
import math
import pygame
import settings
from src.entity.PedestrianNPC import PedestrianNPC

class PedestrianSystem:
    def __init__(self, city_map):
        self.city_map = city_map
        self.npc_nodes = {}
        self.active_npcs = []
        
        # Balance count and spawn timing
        self.max_npcs = getattr(settings, 'PEDESTRIAN_MAX_COUNT', 25)
        self.spawn_timer = 0.0
        self.spawn_interval = getattr(settings, 'PEDESTRIAN_SPAWN_INTERVAL', 1.0)
        self.camera = None
        
        self._load_npc_nodes()

    def _load_npc_nodes(self):
        """Loads all nodes from the nodes layer and indexes npc_ nodes."""
        nodes_layer = self.city_map.tilemap.object_layers.get("nodes", [])
        for obj in nodes_layer:
            center_x = obj.x + getattr(obj, "width", 0) / 2
            center_y = obj.y + getattr(obj, "height", 0) / 2
            
            node_name = obj.name if obj.name else ""
            if not node_name:
                continue

            raw_props = getattr(obj, "properties", {})
            if isinstance(raw_props, dict):
                props = raw_props
            elif isinstance(raw_props, list):
                props = {}
                for p in raw_props:
                    if isinstance(p, dict) and "name" in p:
                        props[p["name"]] = p.get("value")
                    elif hasattr(p, "name"):
                        props[p.name] = getattr(p, "value", None)
            else:
                props = {}
            
            next_val = props.get("next", "")
            if isinstance(next_val, str) and next_val.strip():
                next_list = [n.strip() for n in next_val.split(",") if n.strip()]
            else:
                next_list = []
                
            is_despawn = bool(props.get("despawn", False))
            dir_despawn = props.get("dir_despawn", "up")
            
            self.npc_nodes[node_name] = {
                "x": center_x,
                "y": center_y,
                "next": next_list,
                "despawn": is_despawn,
                "dir_despawn": dir_despawn
            }

        # Validate and sanitize all node connections:
        # Discard typo edges (> 600px) and edges cutting through building interiors
        col_rects = getattr(self.city_map, "collision_rects", [])
        deflated_rects = [r.inflate(-6, -6) for r in col_rects if r.width > 8 and r.height > 8]
        
        for name, data in self.npc_nodes.items():
            p1 = (data["x"], data["y"])
            valid_next = []
            for n in data["next"]:
                if n == name:
                    continue # No self loops
                target_pos = self.get_node_pos(n)
                if not target_pos:
                    continue # Target node does not exist
                
                dx = target_pos[0] - p1[0]
                dy = target_pos[1] - p1[1]
                if (dx * dx + dy * dy) > (600.0 * 600.0):
                    continue # Discard typo edges across the entire city
                    
                # Discard edges cutting through building interiors
                cuts_building = False
                for r in deflated_rects:
                    if r.clipline(p1, target_pos):
                        cuts_building = True
                        break
                if not cuts_building:
                    valid_next.append(n)
                    
            data["next"] = valid_next
            if not valid_next:
                data["despawn"] = True

    def get_npc_node(self, name: str):
        return self.npc_nodes.get(name)

    def get_node_pos(self, name: str):
        info = self.npc_nodes.get(name)
        if info:
            return (info["x"], info["y"])
        # Fallback to city_map.nodes if it's a landmark
        if name in self.city_map.nodes:
            return self.city_map.nodes[name]
        return None

    def get_nearby_cars(self, x: float, y: float, radius: float = 70.0):
        """Returns all vehicles (traffic and player) within radius of (x, y)."""
        nearby = []
        radius_sq = radius * radius
        
        # Check active traffic cars with AABB box filter first
        if hasattr(self.city_map, "traffic_system") and self.city_map.traffic_system:
            for car in self.city_map.traffic_system.active_cars:
                dx = car.x - x
                if abs(dx) > radius:
                    continue
                dy = car.y - y
                if abs(dy) > radius:
                    continue
                if (dx * dx + dy * dy) <= radius_sq:
                    nearby.append(car)
                    
        # Check taxi if available
        taxi = getattr(self.city_map, "taxi", None)
        if taxi:
            dx = taxi.x - x
            dy = taxi.y - y
            if abs(dx) <= radius and abs(dy) <= radius and (dx * dx + dy * dy) <= radius_sq:
                nearby.append(taxi)
            
        return nearby

    def update(self, dt: float, camera=None):
        self.camera = camera
        
        # Despawn dead NPCs or NPCs extremely far away from the player
        remaining_npcs = []
        cam_x = getattr(camera, 'x', 0) if camera else 0
        cam_y = getattr(camera, 'y', 0) if camera else 0
        max_dist = getattr(settings, 'PEDESTRIAN_MAX_DISTANCE', 900)
        max_dist_sq = max_dist * max_dist
        
        # Screen visibility bounds for skipping offscreen hazard queries
        view_margin_x = (settings.VIRTUAL_WIDTH / 2) + 60
        view_margin_y = (settings.VIRTUAL_HEIGHT / 2) + 60
        
        for npc in self.active_npcs:
            if npc.state == "dead":
                continue
                
            dx = npc.x - cam_x
            dy = npc.y - cam_y
            
            if camera:
                if (dx * dx + dy * dy) > max_dist_sq:
                    continue # Discard far away NPC
                    
                is_on_screen = (abs(dx) <= view_margin_x) and (abs(dy) <= view_margin_y)
            else:
                is_on_screen = True
                    
            npc.update(dt, is_on_screen=is_on_screen)
            if npc.state != "dead":
                remaining_npcs.append(npc)
                
        self.active_npcs = remaining_npcs
        
        # Spawning logic
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            spawn_chance = getattr(settings, 'PEDESTRIAN_SPAWN_CHANCE', 0.65)
            if random.random() <= spawn_chance and len(self.active_npcs) < self.max_npcs and self.npc_nodes:
                self.try_spawn_npc()

    def try_spawn_npc(self):
        # We prefer spawning at npc_ nodes
        candidate_nodes = [name for name in self.npc_nodes.keys() if name.startswith("npc_")]
        if not candidate_nodes:
            candidate_nodes = list(self.npc_nodes.keys())
            
        if not candidate_nodes:
            return
            
        if self.camera:
            cam_x, cam_y = getattr(self.camera, 'x', 0), getattr(self.camera, 'y', 0)
            # Must spawn slightly outside the visible screen so they don't pop into view
            margin_x = (settings.VIRTUAL_WIDTH / 2) + 40
            margin_y = (settings.VIRTUAL_HEIGHT / 2) + 40
            spawn_range = getattr(settings, 'PEDESTRIAN_SPAWN_RANGE', 550)
            spawn_range_sq = spawn_range * spawn_range
            
            def is_good_spawn(name):
                node_data = self.npc_nodes[name]
                nx, ny = node_data["x"], node_data["y"]
                dx = nx - cam_x
                dy = ny - cam_y
                in_view = (abs(dx) <= margin_x) and (abs(dy) <= margin_y)
                if in_view:
                    return False
                if (dx * dx + dy * dy) > spawn_range_sq:
                    return False
                # Must have at least one valid next path to walk towards
                if not node_data.get("next"):
                    return False
                # Ensure no car is on top of or near this spawn node
                nearby_cars = self.get_nearby_cars(nx, ny, radius=50.0)
                if nearby_cars:
                    return False
                return True
                
            valid_candidates = [n for n in candidate_nodes if is_good_spawn(n)]
            if valid_candidates:
                candidate_nodes = valid_candidates
            else:
                # If no ideal node found nearby offscreen, wait for next tick
                return
                
        spawn_node = random.choice(candidate_nodes)
        node_pos = (self.npc_nodes[spawn_node]["x"], self.npc_nodes[spawn_node]["y"])
        
        # Final safety check: if a car drove over the node, abort spawn
        if self.get_nearby_cars(node_pos[0], node_pos[1], radius=50.0):
            return
            
        npc = PedestrianNPC(node_pos[0], node_pos[1], spawn_node, self)
        self.active_npcs.append(npc)

    def render(self, surface: pygame.Surface, camera=None):
        if camera:
            cam_x, cam_y = getattr(camera, 'x', 0), getattr(camera, 'y', 0)
            # Render slightly before entering screen so they appear smoothly
            cull_margin_x = (settings.VIRTUAL_WIDTH / 2) + 80
            cull_margin_y = (settings.VIRTUAL_HEIGHT / 2) + 80
            
            for npc in self.active_npcs:
                if abs(npc.x - cam_x) <= cull_margin_x and abs(npc.y - cam_y) <= cull_margin_y:
                    npc.render(surface, camera)
        else:
            for npc in self.active_npcs:
                npc.render(surface, camera)
