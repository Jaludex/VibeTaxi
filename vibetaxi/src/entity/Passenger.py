import math
import pygame
import settings
from gale.animation import Animation
from src.entity.Entity import Entity

class Passenger(Entity):
    def __init__(self, x: float, y: float, destination_node: str, definition: dict):
        self.destination = destination_node
        self.radius = settings.PASSENGER_DETECTION_RADIUS
        self.state = "waiting"
        self.target_taxi = None
        
        self.animations = {}
        self.current_animation = None
        self.flipped = False
        
        entity_def = definition
        
        super().__init__(x, y, entity_def)
        
        if "animations" in definition:
            self.generate_animations(definition["animations"])
            self.change_animation("idle")

    def generate_animations(self, animation_defs: dict) -> None:
        for animation_id, values in animation_defs.items():
            animation = Animation(
                values["frames"],
                values.get("interval", 0),
                loops=values.get("loops"),
            )
            self.animations[animation_id] = animation

    def change_animation(self, animation_id: str) -> None:
        new_animation = self.animations.get(animation_id)
        if new_animation and new_animation != self.current_animation:
            self.current_animation = new_animation
            self.current_animation.reset()
            self.frame_index = self.current_animation.get_current_frame()

    def update(self, dt: float):
        if self.current_animation:
            self.current_animation.update(dt)
            self.frame_index = self.current_animation.get_current_frame()
            
        if self.state == "entering" and self.target_taxi:
            dx = self.target_taxi.x - self.x
            dy = self.target_taxi.y - self.y
            distance = math.hypot(dx, dy)
            
            self.flipped = dx < 0
            
            if distance < 5.0:
                self.state = "riding"
            else:
                move_speed = 100 * dt
                self.x += (dx / distance) * move_speed
                self.y += (dy / distance) * move_speed
                
        elif self.state == "leaving" and hasattr(self, "target_dest_pos"):
            target_x, target_y = self.target_dest_pos
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.hypot(dx, dy)
            
            self.flipped = dx < 0
            
            if distance < 5.0:
                self.state = "done"
            else:
                move_speed = 100 * dt
                self.x += (dx / distance) * move_speed
                self.y += (dy / distance) * move_speed