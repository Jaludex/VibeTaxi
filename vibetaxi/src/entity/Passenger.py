import math
import settings
import random
from gale.animation import Animation
from gale.state import StateMachine
from src.entity.Entity import Entity

from src.states.entity.PassengerWaitState import PassengerWaitState
from src.states.entity.PassengerWalkState import PassengerWalkState
from src.states.entity.PassengerRideState import PassengerRideState
from src.definitions.passenger_dialogues import DIALOGUES_BANK
from src.definitions.comfort import COMFORT_RULES
from src.definitions.radio import RADIO_STATIONS

class Passenger(Entity):
    def __init__(self, x: float, y: float, destination_node: str, destination_pos: tuple, definition: dict):
        self.destination = destination_node
        self.definition = definition
        
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
        
        # new systems
        self.music_preference = definition.get("music_preference", "")
        if not self.music_preference:
            valid_genres = [station["genre"] for station in RADIO_STATIONS if station["genre"] != "off"]
            if valid_genres:
                self.music_preference = random.choice(valid_genres)
            self.definition["music_preference"] = self.music_preference
            
        base_greeting = random.choice(DIALOGUES_BANK["enter"]).format(destination=self.destination)
        genre_hints = DIALOGUES_BANK.get("hints", {}).get(self.music_preference, [])
        hint = random.choice(genre_hints) if genre_hints else ""
        greeting = f"{base_greeting} {hint}".strip()
        
        self.dialogues = {
            "enter": greeting,
            "reaction_good": random.choice(DIALOGUES_BANK["reaction"]["good"]),
            "reaction_neutral": random.choice(DIALOGUES_BANK["reaction"]["neutral"]),
            "reaction_bad": random.choice(DIALOGUES_BANK["reaction"]["bad"]),
            "exit_good": random.choice(DIALOGUES_BANK["exit"]["good"]),
            "exit_bad": random.choice(DIALOGUES_BANK["exit"]["bad"])
        }

        self.comfort = float(random.randint(int(COMFORT_RULES["initial_min"]), int(COMFORT_RULES["initial_max"])))
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
            if is_correct_song and self.time_riding <= COMFORT_RULES["initial_reaction_time"]:
                self.comfort = min(COMFORT_RULES["max_comfort"], self.comfort + COMFORT_RULES["initial_reaction_bonus"])
                self.has_initial_music_reacted = True
                if hud:
                    hud.show_text(random.choice(DIALOGUES_BANK["reaction"]["good"]))
            elif self.time_riding > COMFORT_RULES["initial_reaction_time"]:
                # If player didn't match the music in 4s, stay silent
                self.has_initial_music_reacted = True

        # Continuous comfort increase with matching song
        if is_correct_song:
            rate = COMFORT_RULES.get("comfort_increase_rate", 1.25)
            self.comfort = min(COMFORT_RULES["max_comfort"], self.comfort + rate * dt)
            
    def on_collision(self, hud=None):
        self.comfort = max(COMFORT_RULES["min_comfort"], self.comfort - COMFORT_RULES["collision_penalty"])
        if hud:
            hud.show_text(random.choice(DIALOGUES_BANK["reaction"]["bad"]))
            if hasattr(hud, "trigger_crash"):
                hud.trigger_crash()

        

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