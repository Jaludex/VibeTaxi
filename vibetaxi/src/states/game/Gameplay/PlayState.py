from typing import Dict, Any, TypeVar
import math
import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.physics import BodyType
from gale.state import BaseState
from gale.text import render_text

import settings
from src.world.CityMap import CityMap
from src.entity.Taxi import Taxi
from src.gui.RadioTuner import Radio
from src.definitions.vehicles import VEHICLE_DEFS
from src.gui.PassengerHUD import PassengerHUD
from gale.ui.manager import UIManager
from gale.timer import Timer
from src.definitions.comfort import COMFORT_RULES
from src.mouse_tools import physical_to_virtual
from src.ParticleEmitter import ParticleEmitter
from src.i18n import tr
from src.states.game.Menus.MessageBoxState import MessageBoxState

class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.game_rule_strategy = enter_params.get("game_rule_strategy")
        if self.game_rule_strategy is None:
            # Fallback for testing if not provided
            from src.game_rules.ArcadeStrategy import ArcadeStrategy
            self.game_rule_strategy = ArcadeStrategy()
            
        self.city_map = enter_params.get("city_map")
        if self.city_map is None:
            self.city_map = CityMap("city", enable_pedestrians=True)

        self.tilemap = self.city_map.tilemap

        self.taxi = enter_params.get("taxi")
        if self.taxi is None:
            spawn_x, spawn_y = self.city_map.get_taxi_spawn_position()
            self.taxi = Taxi(spawn_x, spawn_y, VEHICLE_DEFS["yellow_taxi"])
            
        taxi_health = enter_params.get("taxi_health")
        if taxi_health is not None:
            self.taxi.health = taxi_health

        self.taxi.tilemap = self.city_map.tilemap
        self.taxi.city_map = self.city_map
        self.city_map.taxi = self.taxi
        self.taxi.invincible = getattr(self.game_rule_strategy, "invincible", False)
        self.taxi.set_physics(
            self.city_map.physics_world,
            body_type=BodyType.DYNAMIC,
            width=self.taxi.width,
            height=self.taxi.height,
        )

        self.camera = enter_params.get("camera")
        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.taxi, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.city_map.get_rect()
            self.camera.x, self.camera.y = self.taxi.x, self.taxi.y
            self.camera.update(0)

        self.taxi.camera = self.camera
        #radio
        self.radio =  enter_params.get("radio")
        if self.radio is None:
            self.radio = Radio(80, 296)
            
        self.active_passenger = None
        self.map_passengers = self.city_map.generate_passengers(spawn_chance=0.5)
        
        self.nearby_props = []
        self.nearby_passengers = []

        self.soundscape_channel = None
        try:
            soundscape = pygame.mixer.Sound(settings.BASE_DIR / "assets" / "music" / "city_soundscape.mp3")
            self.soundscape_channel = soundscape.play(loops=-1)
            if self.soundscape_channel:
                from src import audio
                self.soundscape_channel.set_volume(0.5 * audio.ambient_scale())
        except Exception as e:
            print("Error loading soundscape:", e)
            
        try:
            engine_start = settings.SOUNDS.get("engine_start")
            if engine_start:
                from src import audio
                ch = engine_start.play()
                if ch: ch.set_volume(0.4 * audio.engine_scale())
        except Exception as e:
            pass
            
        self.taxi.init_sounds()
        self.exited = False
        
        self.danger_color = (255, 0, 0)
        from gale.timer import Timer
        self.danger_timer = Timer.every(0.5, self._toggle_danger_color)
        
        self.fade_overlay_alpha = 255.0
        self.day_text_alpha = 0.0
        self.start_text = self.game_rule_strategy.get_start_text()
        

        self.tutorial_mode = enter_params.get("tutorial_mode", False)
        if self.tutorial_mode:
            self.tutorial_step = 1
            self.tutorial_vibe_shown = False
            self._tutorial_initial_time = getattr(self.game_rule_strategy, "time_remaining", None)

        def on_intro_finished():
            if getattr(self, "tutorial_mode", False) and not getattr(self, "exited", False):
                self.reset_inputs()
                self.state_machine.push(MessageBoxState(
                    self.state_machine,
                    title=tr("tutorial_title"),
                    message=tr("tutorial_integrated_welcome")
                ))

        def fade_out_text():
            Timer.tween(1.0, [(self, {"day_text_alpha": 0.0})], on_finish=on_intro_finished)
            
        Timer.tween(1.0, [(self, {"day_text_alpha": 255.0, "fade_overlay_alpha": 0.0})], on_finish=lambda: Timer.after(2.0, fade_out_text))

    def _toggle_danger_color(self):
        if self.danger_color == (255, 0, 0):
            self.danger_color = (255, 255, 0)
        else:
            self.danger_color = (255, 0, 0)

    def get_discord_presence(self) -> dict:
        if hasattr(self, "game_rule_strategy") and hasattr(self.game_rule_strategy, "get_discord_presence"):
            return self.game_rule_strategy.get_discord_presence(self)
        return {
            "details": "In-game",
            "state": "Driving through the city",
        }

    def fixed_update(self) -> None:
        if getattr(self, "game_over_triggered", False):
            return
        self.city_map.fixed_update()

    def update(self, dt):
        if getattr(self, "game_over_triggered", False):
            return

        # Check pause on window focus loss
        if not hasattr(self, "_had_focus"):
            self._had_focus = True
        has_focus = pygame.key.get_focused()
        if self._had_focus and not has_focus:
            from src import config
            if config.get("pause_on_focus_loss", True):
                from src.states.game.Gameplay.PauseState import PauseState
                if not any(isinstance(s, PauseState) for s in self.state_machine.states):
                    self.pause_audio()
                    self.state_machine.push(PauseState(self.state_machine))
                    self._had_focus = False
                    return
        self._had_focus = has_focus
            
        self.taxi.update(dt)
        self.city_map.update(dt, self.camera)

        if hasattr(self.taxi, "get_render_coords"):
            rx, ry = self.taxi.get_render_coords()
            real_x, real_y = self.taxi.x, self.taxi.y
            self.taxi.x, self.taxi.y = rx, ry
            self.camera.update(dt)
            self.taxi.x, self.taxi.y = real_x, real_y
        else:
            self.camera.update(dt)

        self.radio.update(dt)
        
        
        self.game_rule_strategy.update(dt)
        if getattr(self, "tutorial_mode", False):
            if hasattr(self.game_rule_strategy, "time_remaining") and getattr(self, "_tutorial_initial_time", None) is not None:
                self.game_rule_strategy.time_remaining = self._tutorial_initial_time
        
        if hasattr(self.game_rule_strategy, "should_respawn_passengers") and self.game_rule_strategy.should_respawn_passengers(len(self.map_passengers)):
            new_passengers = self.city_map.generate_passengers(spawn_chance=0.3)
            self.map_passengers.extend(new_passengers)
            
        if getattr(self.game_rule_strategy, "always_vibe", False):
            from src.states.entity.TaxiVibeState import TaxiVibeState
            if not isinstance(self.taxi.state_machine.current, TaxiVibeState) and self.taxi.health > 0:
                self.taxi.state_machine.change("vibe")
        
        if (self.taxi.health <= 0 or self.game_rule_strategy.game_over) and not getattr(self, "game_over_triggered", False):
            self.game_over_triggered = True
            
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            
            self.game_rule_strategy.on_game_over(self.state_machine, self.taxi)
            return
        
        self.arrow_time = getattr(self, 'arrow_time', 0.0) + dt
        import math
        self.arrow_offset_y = (math.sin(self.arrow_time * 6.0) + 1.0) * 5.0
        
        # Manage virtual cursor particles (mouse click emitter)
        is_driving = getattr(self.taxi, "is_accelerating", False) and not getattr(self.taxi, "prevent_movement", False)
        
        if is_driving:
            target_x = getattr(self.taxi, "target_x", self.taxi.x)
            target_y = getattr(self.taxi, "target_y", self.taxi.y)
            
            # Don't show particles if target is exactly on top of the car (idle intent)
            dist_to_target = math.hypot(target_x - self.taxi.x, target_y - self.taxi.y)
            if dist_to_target > 5:
                if getattr(self, "_click_emitter", None) is None or not getattr(self._click_emitter, "_is_emitting", False):
                    if getattr(self, "_click_emitter", None) is not None:
                        self._click_emitter.stop()
                    self._click_emitter = ParticleEmitter.create_mouse_click(target_x, target_y)
                    self.city_map.particle_emitters.append(self._click_emitter)
                
                self._click_emitter.x = target_x
                self._click_emitter.y = target_y
            else:
                if getattr(self, "_click_emitter", None) is not None:
                    self._click_emitter.stop()
                    self._click_emitter = None
        else:
            if getattr(self, "_click_emitter", None) is not None:
                self._click_emitter.stop()
                self._click_emitter = None
        
        if self.soundscape_channel:
            from src import audio
            base_vol = 0.5 if self.radio.ind_song == 0 else 0.1
            self.soundscape_channel.set_volume(base_vol * audio.ambient_scale())
        
        if self.camera:
            cam_x, cam_y = self.camera.offset
            zoom = self.camera.zoom
            vw = self.camera.viewport_width / zoom
            vh = self.camera.viewport_height / zoom

            prop_min_x = cam_x - 100
            prop_max_x = cam_x + vw + 100
            prop_min_y = cam_y - 100
            prop_max_y = cam_y + vh + 100

            self.nearby_props = self.city_map.get_nearby_props(
                prop_min_x, prop_max_x, prop_min_y, prop_max_y
            )

            pass_min_x = cam_x - 150
            pass_max_x = cam_x + vw + 150
            pass_min_y = cam_y - 150
            pass_max_y = cam_y + vh + 150

            self.nearby_passengers = [
                p for p in self.map_passengers 
                if pass_min_x <= p.x <= pass_max_x and pass_min_y <= p.y <= pass_max_y
            ]
        else:
            self.nearby_props = self.city_map.props[:]
            self.nearby_passengers = self.map_passengers[:]

        for p in self.nearby_passengers:
            p.update(dt)

        # Check collision between Vehicles (Taxi + Traffic Cars) and Pedestrian NPCs
        if hasattr(self.city_map, "pedestrian_system") and self.city_map.pedestrian_system:
            taxi_rect = self.taxi.get_collision_rect()
            taxi_x = self.taxi.x
            taxi_y = self.taxi.y
            
            cam_x = getattr(self.camera, 'x', taxi_x)
            cam_y = getattr(self.camera, 'y', taxi_y)
            view_margin_x = (settings.VIRTUAL_WIDTH / 2) + 50
            view_margin_y = (settings.VIRTUAL_HEIGHT / 2) + 50
            
            traffic_cars = []
            if hasattr(self.city_map, "traffic_system") and self.city_map.traffic_system:
                traffic_cars = self.city_map.traffic_system.active_cars
            
            for npc in self.city_map.pedestrian_system.active_npcs:
                if npc.state in ("hit", "down", "getting_up", "dead"):
                    continue
                
                # Check collision with Taxi
                if abs(npc.x - taxi_x) <= 35 and abs(npc.y - taxi_y) <= 35:
                    npc_rect = npc.get_collision_rect()
                    if taxi_rect.colliderect(npc_rect):
                        # Trigger knockback toss animation
                        npc.on_hit_by_car(self.taxi.x, self.taxi.y, car_speed=getattr(self.taxi, "speed", 50.0))
                        
                        # Play collision sound and emit impact sparks
                        if not getattr(self.city_map, "muted", False) and "crash_car" in settings.SOUNDS:
                            crash_snd = settings.SOUNDS["crash_car"]
                            crash_snd.set_volume(0.35)
                            crash_snd.play()
                        self.city_map.add_particle_emitter(ParticleEmitter.create_sparks(npc.x, npc.y))
                        
                        # Slow down taxi slightly
                        self.taxi.speed *= 0.8
                        
                        # Penalize passenger comfort if riding
                        if self.active_passenger and self.active_passenger.is_riding():
                            self.active_passenger.on_collision(hud=self.game_rule_strategy.get_hud())
                        continue

                # Cull collision check with traffic cars if NPC is not on screen!
                is_on_screen = (abs(npc.x - cam_x) <= view_margin_x and 
                                abs(npc.y - cam_y) <= view_margin_y)
                if not is_on_screen:
                    continue

                # Check collision with Traffic Cars (only for on-screen NPCs)
                for car in traffic_cars:
                    if abs(npc.x - car.x) <= 35 and abs(npc.y - car.y) <= 35:
                        npc_rect = npc.get_collision_rect()
                        car_rect = car.get_collision_rect()
                        if car_rect.colliderect(npc_rect):
                            npc.on_hit_by_car(car.x, car.y, car_speed=getattr(car, "speed", 30.0))
                            car.speed = 0.0
                            car.is_braking = True
                            
                            if not getattr(self.city_map, "muted", False) and "crash_car" in settings.SOUNDS:
                                crash_snd = settings.SOUNDS["crash_car"]
                                crash_snd.set_volume(0.25)
                                crash_snd.play()
                            self.city_map.add_particle_emitter(ParticleEmitter.create_sparks(npc.x, npc.y))
                            break

        if self.active_passenger:
            self.update_active_passenger(dt)
        else:
            self.update_city_passengers(dt)
            
        # Vibe transitions
        is_vibe = type(self.taxi.state_machine.current).__name__ == "TaxiVibeState"
        was_vibe = getattr(self, "was_vibe", False)
        
        if not hasattr(self, "vibe_alpha"):
            self.vibe_alpha = 0.0
            self.vibe_color = None
            
        if is_vibe:
            genre = self.radio.get_current_genre()
            if genre and genre in settings.VIBE_COLORS:
                self.vibe_color = settings.VIBE_COLORS[genre]
                self.taxi.vibe_color = self.vibe_color
            
        from src import audio
        if is_vibe and not was_vibe:
            audio.play_sfx("into_vibe")
            Timer.tween(0.5, [(self, {"vibe_alpha": 40.0})])
        elif not is_vibe and was_vibe:
            audio.play_sfx("out_vibe")
            Timer.tween(0.5, [(self, {"vibe_alpha": 0.0})])
            
        self.was_vibe = is_vibe
            
    def update_active_passenger(self, dt: float):
        if not self.active_passenger:
            self.taxi.prevent_movement = False
            return
            
        self.active_passenger.update(dt)

        if not self.active_passenger:
            self.taxi.prevent_movement = False
            return

        if self.active_passenger.is_walking():
            self.taxi.is_accelerating = False
            self.taxi.prevent_movement = True
        else:
            self.taxi.prevent_movement = False

        if self.active_passenger.is_riding():
            
            song_actual = self.radio.get_current_genre()
            self.active_passenger.update_comfort(dt, song_actual, self.game_rule_strategy.get_hud())

            # Detect taxi damage since last frame and notify passenger
            prev_health = getattr(self, "_prev_taxi_health", self.taxi.health)
            if self.taxi.health < prev_health:
                self.active_passenger.on_collision(hud=self.game_rule_strategy.get_hud())
            self._prev_taxi_health = self.taxi.health
                
            from src.states.entity.TaxiVibeState import TaxiVibeState
            if not getattr(self.game_rule_strategy, "always_vibe", False):
                if self.active_passenger.comfort >= COMFORT_RULES["vibe_threshold"]:
                    if not isinstance(self.taxi.state_machine.current, TaxiVibeState):
                        self.taxi.state_machine.change("vibe")
                else:
                    if isinstance(self.taxi.state_machine.current, TaxiVibeState):
                        self.taxi.state_machine.change("drive")

            if (getattr(self, "tutorial_mode", False) and 
                getattr(self, "tutorial_step", 1) == 2 and 
                not getattr(self, "tutorial_vibe_shown", False)):
                if isinstance(self.taxi.state_machine.current, TaxiVibeState):
                    self.tutorial_vibe_shown = True
                    self.reset_inputs()
                    self.state_machine.push(MessageBoxState(
                        self.state_machine,
                        title=tr("tutorial_title"),
                        message=tr("tutorial_integrated_vibe")
                    ))

            dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
            dx = self.taxi.x - dest_x
            dy = self.taxi.y - dest_y
            distance = math.hypot(dx, dy)
            
            if distance <= 80 and abs(self.taxi.speed) < 5:
                # Capture variables for closure
                p = self.active_passenger
                distance_traveled = math.hypot(dest_x - p.pickup_x, dest_y - p.pickup_y)
                
                def reach_destination():
                    self.game_rule_strategy.on_passenger_delivered(p, distance_traveled)
                    self.active_passenger = None
                    
                    # Exit vibe if we were in it, unless in Zen mode
                    from src.states.entity.TaxiVibeState import TaxiVibeState
                    if not getattr(self.game_rule_strategy, "always_vibe", False):
                        if isinstance(self.taxi.state_machine.current, TaxiVibeState):
                            self.taxi.state_machine.change("drive")


                    if getattr(self, "tutorial_mode", False) and getattr(self, "tutorial_step", 1) == 2:
                        self.tutorial_step = 3
                        self.tutorial_mode = False
                        settings.TUTORIAL_ENABLED = False
                        self.reset_inputs()
                        self.state_machine.push(MessageBoxState(
                            self.state_machine,
                            title=tr("tutorial_completed_title"),
                            message=tr("tutorial_integrated_complete")
                        ))

                from src import audio
                audio.play_sfx("money")

                self.active_passenger.state_machine.change(
                    "walk", 
                    target=(dest_x, dest_y), 
                    on_arrival=reach_destination
                )
                self.game_rule_strategy.unbind_passenger()

    def update_city_passengers(self, dt: float):
        for p in self.map_passengers:
            if p.is_waiting():
                dx = self.taxi.x - p.x
                dy = self.taxi.y - p.y
                distance = math.hypot(dx, dy)
                
                if distance <= settings.PASSENGER_DETECTION_RADIUS and abs(self.taxi.speed) < 5:
                    def reach_taxi():
                        p.state_machine.change("ride", taxi=self.taxi)
                        self._prev_taxi_health = self.taxi.health  # baseline for crash detection
                        self.arrow_radius_progress = 0.0
                        Timer.tween(0.7, [(self, {"arrow_radius_progress": 1.0})], ease_function_name="out_cubic")
                        
                        if getattr(self, "tutorial_mode", False) and getattr(self, "tutorial_step", 1) == 1:
                            self.tutorial_step = 2
                            self.reset_inputs()
                            self.game_rule_strategy.bind_passenger(p, show_dialogue=False)
                            
                            def on_radio_dialog_closed():
                                self.game_rule_strategy.show_passenger_greeting()

                            self.state_machine.push(MessageBoxState(
                                self.state_machine,
                                title=tr("tutorial_title"),
                                message=tr("tutorial_integrated_radio"),
                                on_close=on_radio_dialog_closed
                            ))
                        else:
                            self.game_rule_strategy.bind_passenger(p, show_dialogue=True)
                    
                    from src import audio
                    audio.play_sfx("honk")
                        
                    p.state_machine.change("walk", target=self.taxi, on_arrival=reach_taxi)
                    self.active_passenger = p
                    self.map_passengers.remove(p)
                    
                    p.pickup_x = p.x
                    p.pickup_y = p.y
                    if settings.PHYSICS_DEBUG:
                        print(f"DEBUG: New active passenger. Preferred genre: {p.music_preference if p.music_preference else 'off'}")
                    break

    def render(self, surface):
        self.city_map.render_layers(surface, self.camera, settings.TILED_GROUND_LAYERS)
        for emitter in self.city_map.particle_emitters:
            if getattr(emitter, "is_ground", False):
                emitter.render(surface, self.camera)

        render_active_passenger = False

        if self.active_passenger:
            if self.active_passenger.is_riding():
                dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
                self._render_detection_circle(surface, dest_x, dest_y, settings.PASSENGER_DELIVERY_RADIUS, settings.COLOR_PASSENGER_DELIVERY)
            
            if self.active_passenger.is_walking():
                render_active_passenger = True
        else:
            for p in self.nearby_passengers:
                if p.is_waiting():
                    self._render_detection_circle(surface, p.x, p.y, settings.PASSENGER_DETECTION_RADIUS, (255, 255, 0))

        self.city_map.render_layers(surface, self.camera, settings.TILED_MIDDLE_LAYERS)

        for prop in self.nearby_props:
            prop.render(surface, self.camera)
            
        for p in self.nearby_passengers:
            p.render(surface, self.camera)

        if render_active_passenger:
            self.active_passenger.render(surface, self.camera)
            
        self.city_map.render_pedestrians(surface, self.camera)
        self.city_map.render_traffic(surface, self.camera)
        self.taxi.render(surface, self.camera)
        for emitter in self.city_map.particle_emitters:
            if not getattr(emitter, "is_ground", False) and not getattr(emitter, "is_ui", False):
                emitter.render(surface, self.camera)

        self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_NO_SHADOW_LAYERS)
        self.city_map.render_layers(surface, self.camera, settings.TILED_UPPER_SHADOW_LAYERS)
        self.city_map.render_car_silhouette_if_obstructed(surface, self.taxi, self.camera)

        # Physics debug overlay
        try:
            if settings.PHYSICS_DEBUG:
                self.city_map.render_debug(surface, self.camera)
                
                # Render gamepad deadzone circle on the taxi
                from src.input_strategies import GamepadInputStrategy
                if isinstance(self.taxi.input_strategy, GamepadInputStrategy):
                    deadzone = getattr(settings, 'GAMEPAD_DEADZONE', 0.25)
                    max_dist = getattr(settings, 'MOUSE_MAX_SPEED_RADIUS', 80)
                    self._render_detection_circle(surface, self.taxi.x, self.taxi.y, deadzone * max_dist, (255, 100, 100))
        except Exception:
            pass

        # Vibe filter
        vibe_alpha = getattr(self, "vibe_alpha", 0.0)
        vibe_color = getattr(self, "vibe_color", None)
        if vibe_alpha > 0 and vibe_color:
            filter_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            filter_surf.fill((*vibe_color, int(vibe_alpha)))
            surface.blit(filter_surf, (0, 0))

        self.radio.render(surface)
        if self.active_passenger and self.active_passenger.is_riding():
            dest_x, dest_y = self.city_map.nodes[self.active_passenger.destination]
            self._render_arrow(surface, dest_x, dest_y)
        elif getattr(self, "tutorial_mode", False) and getattr(self, "tutorial_step", 1) == 1 and not self.active_passenger:
            nearest_p = self._get_nearest_waiting_passenger()
            if nearest_p:
                self._render_arrow(surface, nearest_p.x, nearest_p.y)
            
        for emitter in self.city_map.particle_emitters:
            if getattr(emitter, "is_ui", False):
                emitter.render(surface, self.camera)
                
        if self.taxi.health < self.taxi.max_health * 0.15:
            from gale.text import render_text
            render_text(
                surface,
                "Danger!",
                settings.FONTS["big"],
                settings.VIRTUAL_WIDTH // 2,
                30,
                self.danger_color,
                center=True,
                shadowed=True
            )
            
        self.game_rule_strategy.render_ui(surface, settings.FONTS["minecraft"], 20, 20)
        
        fade_alpha = getattr(self, "fade_overlay_alpha", 0)
        if fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(fade_alpha)))
            surface.blit(fade_surf, (0, 0))
            
        text_alpha = getattr(self, "day_text_alpha", 0)
        if text_alpha > 0:
            text_layer = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            
            lines = getattr(self, "start_text", "").split('\n')
            center_y = settings.VIRTUAL_HEIGHT / 2

            total_height = len(lines) * settings.FONTS["big"].get_linesize()
            start_y = center_y - total_height / 2 + settings.FONTS["big"].get_height() / 2

            from gale.text import render_text
            
            for i, line in enumerate(lines):
                render_text(
                    text_layer,
                    line,
                    settings.FONTS["big"],
                    settings.VIRTUAL_WIDTH / 2,
                    start_y + i * settings.FONTS["big"].get_linesize(),
                    (255, 255, 255),
                    center=True,
                    shadowed=True
                )
            
            text_layer.set_alpha(int(text_alpha))
            surface.blit(text_layer, (0, 0))
        
    def _render_detection_circle(self, surface, x, y, radius, color):
        if self.camera:
            rect = self.camera.apply(pygame.Rect(x, y, 0, 0))
            px, py = rect.x, rect.y
        else:
            px, py = x, y
        pygame.draw.circle(surface, color, (px, py), radius, width=2)

    def _get_nearest_waiting_passenger(self):
        waiting = [p for p in self.map_passengers if p.is_waiting()]
        if not waiting:
            return None
        return min(waiting, key=lambda p: math.hypot(self.taxi.x - p.x, self.taxi.y - p.y))

    def _render_arrow(self, surface, dest_x, dest_y):
        arrow_tex = settings.TEXTURES.get("arrow")
        if not arrow_tex: return
        
        cam_x, cam_y = self.camera.offset
        cam_w, cam_h = settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT
        
        center_x = self.camera.x
        center_y = self.camera.y
        
        margin = 20
        if (cam_x + margin <= dest_x <= cam_x + cam_w - margin) and \
           (cam_y + margin <= dest_y <= cam_y + cam_h - margin):
            rotated_arrow = pygame.transform.rotate(arrow_tex, -90)
            rect = rotated_arrow.get_rect(center=(dest_x - cam_x, dest_y - cam_y - 40 + getattr(self, "arrow_offset_y", 0)))
            surface.blit(rotated_arrow, rect.topleft)
        else:
            import math
            dx = dest_x - center_x
            dy = dest_y - center_y
            angle = math.atan2(dy, dx)
            
            rotated_arrow = pygame.transform.rotate(arrow_tex, -math.degrees(angle))
            
            # Reduced margin from edge to avoid overlapping with UI elements like the timer
            half_w = cam_w / 2 - 10
            half_h = cam_h / 2 - 10
            
            r_x = float('inf')
            if math.cos(angle) != 0:
                r_x = abs(half_w / math.cos(angle))
            r_y = float('inf')
            if math.sin(angle) != 0:
                r_y = abs(half_h / math.sin(angle))
                
            target_r = min(r_x, r_y)
            
            # Animate radius outward using arrow_radius_progress
            progress = getattr(self, 'arrow_radius_progress', 1.0)
            
            # Start near the taxi (radius 40) and travel to the edge
            r = 40 + (target_r - 40) * progress
            
            screen_pos_x = (cam_w / 2) + r * math.cos(angle)
            screen_pos_y = (cam_h / 2) + r * math.sin(angle)
            
            rect = rotated_arrow.get_rect(center=(screen_pos_x, screen_pos_y))
            surface.blit(rotated_arrow, rect.topleft)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if getattr(self, "game_over_triggered", False):
            return
            
        if input_id == "pause" and input_data.pressed:
            from src import audio
            audio.play_sfx("pause")
            from src.states.game.Gameplay.PauseState import PauseState
            self.state_machine.push(PauseState(self.state_machine))
            return
            
        self.radio.on_input(input_id, input_data)
        self.taxi.on_input(input_id, input_data)

    def pause_audio(self) -> None:
        if hasattr(self, 'soundscape_channel') and self.soundscape_channel:
            try:
                self.soundscape_channel.pause()
            except Exception:
                pass
        if hasattr(self, 'taxi') and self.taxi:
            self.taxi.pause_sounds()
        pygame.mixer.music.pause()

    def resume_audio(self) -> None:
        if hasattr(self, 'soundscape_channel') and self.soundscape_channel:
            try:
                self.soundscape_channel.unpause()
            except Exception:
                pass
        if hasattr(self, 'taxi') and self.taxi:
            self.taxi.resume_sounds()
        pygame.mixer.music.unpause()

    def reset_inputs(self) -> None:
        if hasattr(self, 'taxi') and self.taxi:
            self.taxi.is_accelerating = False
            self.taxi.is_reversing = False
            self.taxi.is_braking = False
            self.taxi.is_drifting = False
            if hasattr(self.taxi, 'state_machine') and self.taxi.state_machine.current:
                if type(self.taxi.state_machine.current).__name__ == "TaxiDriveState":
                    self.taxi.state_machine.change("idle")
        if getattr(self, "_click_emitter", None) is not None:
            self._click_emitter.stop()
            self._click_emitter = None

    def exit(self) -> None:
        self.exited = True
        self.reset_inputs()
        if hasattr(self, '_tutorial_timer') and self._tutorial_timer:
            self._tutorial_timer.remove()
        if hasattr(self, 'danger_timer') and self.danger_timer:
            self.danger_timer.remove()
        if hasattr(self, 'soundscape_channel') and self.soundscape_channel:
            self.soundscape_channel.stop()
        if hasattr(self, 'taxi') and self.taxi:
            self.taxi.stop_sounds()
        pygame.mixer.music.stop()
