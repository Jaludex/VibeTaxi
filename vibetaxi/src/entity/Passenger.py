import math
import settings
from gale.animation import Animation
from gale.state import StateMachine
from src.entity.Entity import Entity

from src.states.entity.PassengerWaitState import PassengerWaitState
from src.states.entity.PassengerWalkState import PassengerWalkState
from src.states.entity.PassengerRideState import PassengerRideState

class Passenger(Entity):
    def __init__(self, x: float, y: float, destination_node: str, destination_pos: tuple, definition: dict):
        self.destination = destination_node
        
        dest_x, dest_y = destination_pos
        trip_distance = math.hypot(dest_x - x, dest_y - y)
        
        if trip_distance < 800:
            self.trip_color = settings.COLOR_TRIP_SHORT
        elif trip_distance < 2000:
            self.trip_color = settings.COLOR_TRIP_MEDIUM
        else:
            self.trip_color = settings.COLOR_TRIP_LONG
        
        self.animations = {}
        self.current_animation = None
        self.flipped = False
        
        super().__init__(x, y, definition)
        
        if "animations" in definition:
            self.generate_animations(definition["animations"])

        self.state_machine = StateMachine({
            "wait": lambda sm: PassengerWaitState(self, sm),
            "walk": lambda sm: PassengerWalkState(self, sm),
            "ride": lambda sm: PassengerRideState(self, sm),
        })
        self.state_machine.change("wait")

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
            
        self.state_machine.update(dt)
        super().update(dt)

    def is_waiting(self) -> bool:
        return isinstance(self.state_machine.current, PassengerWaitState)

    def is_riding(self) -> bool:
        return isinstance(self.state_machine.current, PassengerRideState)

    def is_walking(self) -> bool:
        return isinstance(self.state_machine.current, PassengerWalkState)