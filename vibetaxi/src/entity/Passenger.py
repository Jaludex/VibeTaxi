import settings
import random
from gale.animation import Animation
from gale.state import StateMachine
from src.entity.Entity import Entity

from src.states.entity.PassengerWaitState import PassengerWaitState
from src.states.entity.PassengerWalkState import PassengerWalkState
from src.states.entity.PassengerRideState import PassengerRideState

class Passenger(Entity):
    def __init__(self, x: float, y: float, destination_node: str, definition: dict):
        self.destination = destination_node
        self.definition = definition
        
        self.dialogues = {
            "enter": random.choice(settings.DIALOGUES_BANK["enter"]),
            "reaction_good": random.choice(settings.DIALOGUES_BANK["reaction"]["good"]),
            "reaction_neutral": random.choice(settings.DIALOGUES_BANK["reaction"]["neutral"]),
            "reaction_bad": random.choice(settings.DIALOGUES_BANK["reaction"]["bad"]),
            "exit_good": random.choice(settings.DIALOGUES_BANK["exit"]["good"]),
            "exit_bad": random.choice(settings.DIALOGUES_BANK["exit"]["bad"])
        }
        
        self.animations = {}
        self.current_animation = None
        self.flipped = False
        
        # new systems
        self.music_preference = definition.get("music_preference", "")
        if not self.music_preference:
            self.music_preference = random.choice(settings.MUSIC_GENRES)
            self.definition["music_preference"] = self.music_preference

        self.comfort = float(random.randint(40, 60))
        self.time_riding = 0.0
        self.has_initial_music_reacted = False
        self.periodic_timer = 0.0
        
        super().__init__(x, y, definition)
        
        if "animations" in definition:
            self.generate_animations(definition["animations"])

        self.state_machine = StateMachine({
            "wait": lambda sm: PassengerWaitState(self, sm),
            "walk": lambda sm: PassengerWalkState(self, sm),
            "ride": lambda sm: PassengerRideState(self, sm),
        })
        self.state_machine.change("wait")

    def update_comfort(self, dt: float, current_song: str, hud) -> None:
        if not self.is_riding():
            return
        
        self.time_riding += dt
        is_correct_song = (current_song == self.music_preference)
        
        # Initial 4s window: bonus +20 if matching song is played
        if not self.has_initial_music_reacted:
            if is_correct_song and self.time_riding <= 4.0:
                self.comfort = min(100.0, self.comfort + 20.0)
                self.has_initial_music_reacted = True
                if hud:
                    hud.show_text(random.choice(settings.DIALOGUES_BANK["reaction"]["good"]))
            elif self.time_riding > 4.0:
                # If player didn't match the music in 4s, stay silent
                self.has_initial_music_reacted = True

        # Periodic comfort (+5 every 4s with matching song)
        if is_correct_song:
            self.periodic_timer += dt
            if self.periodic_timer >= 4.0:
                self.comfort = min(100.0, self.comfort + 5.0)
                self.periodic_timer = 0.0
        else:
            self.periodic_timer = 0.0
            
    def on_collision(self, hud=None):
        self.comfort = max(0.0, self.comfort - 25.0)
        if hud:
            hud.show_text(random.choice(settings.DIALOGUES_BANK["reaction"]["bad"]))
        

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