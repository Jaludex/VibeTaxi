from typing import Dict, Any, List
import pygame
from gale.timer import Timer
from gale.input_handler import InputData

from src.states.game.Gameplay.PlayState import PlayState
from src.world.CityMap import CityMap
from src.states.game.Menus.MessageBoxState import MessageBoxState
from src.states.game.Menus.TitleScreenState import TitleScreenState
from src.entity.Passenger import Passenger
from src.definitions.passengers import PASSENGER_DEFS
from src.i18n import tr
import settings

class TutorialPlayState(PlayState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        # Force tutorial map
        if "city_map" not in enter_params or enter_params["city_map"] is None:
            enter_params["city_map"] = CityMap("tutorial")
            
        super().enter(**enter_params)
        
        # Custom tutorial passengers setup
        self.map_passengers = self._create_tutorial_passengers()
        
        # Load tutorial triggers
        self.tutorial_triggers = []
        for obj in self.tilemap.object_layers.get("tutorial_triggers", []):
            self.tutorial_triggers.append({
                "rect": pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                "message": obj.properties.get("message", "No message provided."),
                "condition": obj.properties.get("condition", "")
            })
            
        self.last_checkpoint = (self.taxi.x, self.taxi.y)
        self.tutorial_paused = False
        self.fade_alpha = 0.0

    def _create_tutorial_passengers(self) -> List[Passenger]:
        passengers = []
        
        # 1. Pasajero en City Entrance -> Cornered C.O
        if "City Entrance" in self.city_map.nodes and "Cornered C.O" in self.city_map.nodes:
            spawn_x, spawn_y = self.city_map.nodes["City Entrance"]
            dest_name = "Cornered C.O"
            dest_pos = self.city_map.nodes[dest_name]
            def1 = PASSENGER_DEFS["pedestrian_1"].copy()
            def1["music_preference"] = "pop"
            p1 = Passenger(spawn_x, spawn_y, dest_name, dest_pos, def1)
            passengers.append(p1)
            
        # 2. Pasajero en Long Avenue -> City Endhole
        if "Long Avenue" in self.city_map.nodes and "City Endhole" in self.city_map.nodes:
            spawn_x, spawn_y = self.city_map.nodes["Long Avenue"]
            dest_name = "City Endhole"
            dest_pos = self.city_map.nodes[dest_name]
            def2 = PASSENGER_DEFS["pedestrian_2"].copy()
            def2["music_preference"] = "rock"
            p2 = Passenger(spawn_x, spawn_y, dest_name, dest_pos, def2)
            passengers.append(p2)
            
        return passengers
        
    def _evaluate_condition(self, condition: str) -> bool:
        if not condition:
            return True
            
        if condition == "is_vibe":
            from src.states.entity.TaxiVibeState import TaxiVibeState
            return isinstance(self.taxi.state_machine.current, TaxiVibeState)

        if condition == "has_delivered_a_passenger":
            strategy_delivered = getattr(self.game_rule_strategy, "passengers_delivered", 0)
            return strategy_delivered > 0 or getattr(self, "passengers_delivered", 0) > 0

        if condition == "has_passenger":
            return self.active_passenger is not None and self.active_passenger.is_riding()
            
        print(f"Unknown tutorial condition: {condition}")
        return True # Default to passing if unknown
        
    def _check_tutorial_triggers(self):
        if self.tutorial_paused:
            return
            
        taxi_rect = pygame.Rect(self.taxi.x - 10, self.taxi.y - 10, 20, 20) # Approx bounding box
        
        for trigger in self.tutorial_triggers[:]:
            if taxi_rect.colliderect(trigger["rect"]):
                if self._evaluate_condition(trigger["condition"]):
                    # Passed the checkpoint/trigger
                    self.tutorial_triggers.remove(trigger)
                    self.last_checkpoint = (self.taxi.x, self.taxi.y)
                    
                    # Stop taxi from keeping momentum
                    self.tutorial_paused = True
                    self.taxi.is_accelerating = False
                    self.taxi.is_reversing = False
                    self.taxi.is_braking = False
                    self.taxi.speed = 0.0
                    self.taxi.vx = 0.0
                    self.taxi.vy = 0.0
                    if self.taxi.body is not None:
                        try:
                            self.taxi.body.velocity = (0, 0)
                        except Exception:
                            pass
                    self.taxi.state_machine.change('idle')
                    
                    def on_close():
                        self.tutorial_paused = False
                    
                    self.state_machine.push(MessageBoxState(
                        self.state_machine, 
                        tr("tutorial_title", default="Tutorial"), 
                        tr(trigger["message"]), 
                        on_close=on_close
                    ))
                else:
                    # Failed condition, respawn at last checkpoint
                    self.tutorial_paused = True
                    self.taxi.is_accelerating = False
                    self.taxi.is_reversing = False
                    self.taxi.is_braking = False
                    self.taxi.speed = 0.0
                    self.taxi.vx = 0.0
                    self.taxi.vy = 0.0
                    if self.taxi.body is not None:
                        try:
                            self.taxi.body.velocity = (0, 0)
                        except Exception:
                            pass
                    self.taxi.state_machine.change('idle')
                    
                    self.fade_alpha = 0.0
                    if "crash_car" in settings.SOUNDS:
                        settings.SOUNDS["crash_car"].play()
                        
                    def fade_in():
                        Timer.tween(0.4, [(self, {"fade_alpha": 0.0})], on_finish=lambda: setattr(self, "tutorial_paused", False))
                        
                    def on_fade_out():
                        self.taxi.x, self.taxi.y = self.last_checkpoint
                        if self.taxi.body is not None:
                            self.taxi.body.position = (self.taxi.x, self.taxi.y)
                            self.taxi.body.velocity = (0, 0)
                        if self.camera:
                            self.camera.x, self.camera.y = self.taxi.x, self.taxi.y
                            self.camera.update(0)
                        fade_in()
                        
                    Timer.tween(0.4, [(self, {"fade_alpha": 255.0})], on_finish=on_fade_out)
                    
                break # Only process one trigger per frame

    def _check_tutorial_completion(self):
        if getattr(self, "tutorial_completed", False):
            return
            
        delivered = getattr(self.game_rule_strategy, "passengers_delivered", 0)
        if delivered >= 2 and self.active_passenger is None:
            self.tutorial_completed = True
            self.tutorial_paused = True
            self.taxi.is_accelerating = False
            self.taxi.is_reversing = False
            self.taxi.is_braking = False
            self.taxi.speed = 0.0
            self.taxi.vx = 0.0
            self.taxi.vy = 0.0
            if self.taxi.body is not None:
                try:
                    self.taxi.body.velocity = (0, 0)
                except Exception:
                    pass
            self.taxi.state_machine.change('idle')
            
            def return_to_title():
                while len(self.state_machine.states) > 0:
                    self.state_machine.pop()
                self.state_machine.push(TitleScreenState(self.state_machine))
                
            self.state_machine.push(MessageBoxState(
                self.state_machine,
                tr("tutorial_completed_title", default="Tutorial Completed!"),
                tr("tutorial_completed_msg", default="You have completed the tutorial. Ready for the real work!"),
                on_close=return_to_title
            ))

    def update(self, dt: float):
        if self.tutorial_paused:
            return
        super().update(dt)
        self._check_tutorial_triggers()
        self._check_tutorial_completion()
        
    def fixed_update(self) -> None:
        if self.tutorial_paused:
            return
        super().fixed_update()
        
    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.tutorial_paused:
            return
        super().on_input(input_id, input_data)
        
    def render(self, surface: pygame.Surface) -> None:
        super().render(surface)
        if getattr(self, "fade_alpha", 0.0) > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
