import math
import random
from gale.timer import Timer

def destroy_prop(prop, vehicle):
    prop.collidable = False 
    initial_angle = prop.angle

    rotation_direction = random.choice([1, -1])
    
    prop.pivot_x = (prop.width / 2) * rotation_direction
    prop.pivot_y = prop.height / 2

    Timer.tween(
        0.2,
        [(prop, {"angle": initial_angle + (rotation_direction * (math.pi / 2))})],
        on_finish=lambda: fade_out(prop)
    )

def fade_out(prop):
    def finish():
        # mark inactive and destroy physics body to remove collisions
        try:
            if getattr(prop, 'body', None) is not None:
                prop.body.destroy()
                prop.body = None
        except Exception:
            pass
        setattr(prop, "active", False)

    Timer.tween(
        1.0,
        [(prop, {"alpha": 0})],
        on_finish=finish
    )

from src.ParticleEmitter import ParticleEmitter

def emit_particles_and_destroy(colors, emission_duration: float = 0.0):
    def on_collide(prop, vehicle):
        if not hasattr(prop, 'particle_system') or prop.particle_system is None:
            prop.particle_system = ParticleEmitter(
                prop.x,
                prop.y,
                colors,
                emission_duration=emission_duration,
                lifetime_min=0.2,
                lifetime_max=0.5,
                accel=2.0,
                spread=4.0,
            )
        destroy_prop(prop, vehicle)
    return on_collide

PROPS_DEF = {
    6: {
        "texture": "props",
        "frame": 6,
        "collidable": True,
        "on_collide": destroy_prop
    },
    40: {
        "texture": "props",
        "frame": 40,
        "collidable": True,
        "on_collide": emit_particles_and_destroy(
            [(0, 150, 255, 150), (100, 200, 255, 120)],
            emission_duration=2.0,
        )
    },
    19: {
        "texture": "props",
        "frame": 19,
        "collidable": True,
        "on_collide": emit_particles_and_destroy([(255, 255, 255, 255), (200, 200, 200, 255)])
    },
    4: {
        "texture": "props",
        "frame": 4,
        "collidable": True,
        "on_collide": destroy_prop
    },
    7: {
        "texture": "props",
        "frame": 7,
        "collidable": True,
        "on_collide": emit_particles_and_destroy([(255, 165, 0, 255), (255, 140, 0, 255)])
    },
    36: {
        "texture": "props",
        "frame": 36,
        "collidable": True,
        "on_collide": emit_particles_and_destroy([(255, 255, 255, 255), (200, 200, 200, 255)])
    },
}