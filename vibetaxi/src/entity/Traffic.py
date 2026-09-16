import random
import math
from gale.physics import BodyType, BoxShape
from src.entity.TrafficCar import TrafficCar

import settings

class TrafficSystem:
    def __init__(self, city_map):
        self.city_map = city_map
        self.nodes = {}
        self.active_cars = []
        self.max_cars = getattr(settings, 'TRAFFIC_MAX_CARS', 10)
        self.spawn_timer = 0.0
        self.spawn_interval = getattr(settings, 'TRAFFIC_SPAWN_INTERVAL', 5.0)
        
        self.camera = None # Set this to player's camera if you want distance-based spawning
        
        self._load_traffic_nodes()

    def _load_traffic_nodes(self):
        # Expects Tiled objects in a layer called "traffic-nodes"
        layer = self.city_map.tilemap.object_layers.get("traffic-nodes", [])
        for obj in layer:
            center_x = obj.x + getattr(obj, "width", 0) / 2
            center_y = obj.y + getattr(obj, "height", 0) / 2
            
            # Use 'next' property for the next waypoint
            next_nodes = obj.properties.get("next", "")
            if isinstance(next_nodes, str):
                next_list = [n.strip() for n in next_nodes.split(",") if n.strip()]
            else:
                next_list = []
                
            node_name = obj.name if obj.name else f"traffic_node_{len(self.nodes)}"
            
            self.nodes[node_name] = {
                "x": center_x,
                "y": center_y,
                "next": next_list
            }

    def get_node_position(self, name):
        if name in self.nodes:
            return self.nodes[name]["x"], self.nodes[name]["y"]
        return None
        
    def get_node_next(self, name):
        if name in self.nodes and self.nodes[name]["next"]:
            return random.choice(self.nodes[name]["next"])
        return None

    def update(self, dt, camera=None):
        self.camera = camera
        
        # Update cars
        for car in list(self.active_cars):
            car.update(dt)
            
            # Despawn if too far from camera
            if self.camera:
                cam_x, cam_y = getattr(camera, 'x', 0), getattr(camera, 'y', 0)
                dist = math.hypot(car.x - cam_x, car.y - cam_y)
                if dist > 800: # Far away
                    self.despawn_car(car)
            elif car.crashed and car.speed < 1:
                # Optionally despawn crashed cars if no camera logic
                pass
                
        # Spawning logic
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            if len(self.active_cars) < self.max_cars and self.nodes:
                self.try_spawn_car()
                
    def try_spawn_car(self):
        # Pick a node
        valid_nodes = list(self.nodes.keys())
        
        if self.camera:
            cam_x, cam_y = getattr(self.camera, 'x', 0), getattr(self.camera, 'y', 0)
            # Filter nodes that are outside view but not too far
            def is_good_spawn(name):
                nx, ny = self.nodes[name]["x"], self.nodes[name]["y"]
                dist = math.hypot(nx - cam_x, ny - cam_y)
                return 400 < dist < 700
                
            filtered = [n for n in valid_nodes if is_good_spawn(n)]
            if filtered:
                valid_nodes = filtered
                
        if not valid_nodes:
            return
            
        spawn_node_name = random.choice(valid_nodes)
        spawn_pos = self.get_node_position(spawn_node_name)
        next_node_name = self.get_node_next(spawn_node_name)
        
        if not next_node_name:
            return
            
        next_pos = self.get_node_position(next_node_name)
        if not next_pos:
            return
            
        # Create car (excluding the taxi, which is usually frame 0 / yellow_taxi)
        from src.definitions.vehicles import VEHICLE_DEFS
        valid_keys = [k for k in VEHICLE_DEFS.keys() if k != "yellow_taxi"]
        if not valid_keys:
            valid_keys = list(VEHICLE_DEFS.keys())
            
        car_def_key = random.choice(valid_keys)
        car_def = dict(VEHICLE_DEFS[car_def_key])
        
        # Modify definition to act like traffic
        car_def["max_speed"] *= 0.6 # slower than player
        
        car = TrafficCar(spawn_pos[0], spawn_pos[1], car_def, self)
        car.set_path(next_pos[0], next_pos[1], self.get_node_next(next_node_name))
        
        # Add physics body
        shape = BoxShape(width=car.width, height=car.height, friction=1.0, density=1.0)
        car.set_physics(
            self.city_map.physics_world,
            body_type=BodyType.DYNAMIC,
            shape=shape,
        )
            
        self.active_cars.append(car)
        
    def despawn_car(self, car):
        if car in self.active_cars:
            self.active_cars.remove(car)
        if hasattr(self.city_map.physics_world, '_entity_registry'):
            if car in self.city_map.physics_world._entity_registry:
                self.city_map.physics_world._entity_registry.remove(car)
        if car.body is not None:
            car.body.destroy()

    def render(self, surface, camera=None):
        for car in self.active_cars:
            car.render(surface, camera)
