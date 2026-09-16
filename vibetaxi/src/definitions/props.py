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
        "on_collide": destroy_prop
    },
    19: {
        "texture": "props",
        "frame": 19,
        "collidable": True,
        "on_collide": destroy_prop
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
        "on_collide": destroy_prop
    },
    36: {
        "texture": "props",
        "frame": 36,
        "collidable": True,
        "on_collide": destroy_prop
    },
}