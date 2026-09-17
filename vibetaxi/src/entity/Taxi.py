from gale.state import StateMachine
from typing import Any

from src.entity.Car import Car
from src.states.entity.TaxiIdleState import TaxiIdleState
from src.states.entity.TaxiDriveState import TaxiDriveState
from src.states.entity.TaxiVibeState import TaxiVibeState 

from src.states.entity.CarCrashedState import CarCrashedState

class Taxi(Car):
    def __init__(self, x, y, definition):
        super().__init__(x, y, definition) 

        self.max_health = 100
        self.health = 100
        self.is_accelerating = False
        self.is_crashed = False

        self.state_machine = StateMachine({
            'idle': lambda sm: TaxiIdleState(self, sm),
            'drive': lambda sm: TaxiDriveState(self, sm),
            'vibe': lambda sm: TaxiVibeState(self, sm),
            'crashed': lambda sm: CarCrashedState(self, sm)
        })
        
        from gale.command import CommandBindings
        from src import commands
        
        self.command_bindings = CommandBindings()
        self.command_bindings.bind("mouse_click", press=commands.ACCELERATE, release=commands.STOP_ACCELERATE)
        self.command_bindings.bind("brake", press=commands.BRAKE, release=commands.STOP_BRAKE)
        self.command_bindings.bind("reverse", press=commands.REVERSE, release=commands.STOP_REVERSE)
        self.command_bindings.bind("drift", press=commands.DRIFT, release=commands.STOP_DRIFT)
        
        self.state_machine.change('idle')

    def damage(self, amount):
        if self.health > 0 and not self.is_crashed:
            from src.states.entity.TaxiVibeState import TaxiVibeState
            if isinstance(self.state_machine.current, TaxiVibeState):
                amount *= 0.4 # 60% reduction
            
            self.health = max(0, self.health - amount)
            if self.health <= 0:
                self.is_crashed = True
                self.state_machine.change('crashed')

    def update(self, dt):
        self.state_machine.update(dt)
        super().update(dt)
        
        # Emit smoke if health is below 60%
        if self.health < self.max_health * 0.6:
            import math
            import random
            
            # Create a single emitter instance if we don't have one
            if not hasattr(self, 'engine_smoke_emitter') or not self.engine_smoke_emitter:
                from src.ParticleEmitter import ParticleEmitter
                self.engine_smoke_emitter = ParticleEmitter(
                    0, 0, 
                    colors=[],
                    emission_duration=0,
                    single_burst_count=0,
                    lifetime_min=0.4,
                    lifetime_max=1.0,
                    accel=1.5,
                    spread=4.0,
                    particle_size=4
                )
                self.engine_smoke_emitter.is_permanent = True
                if hasattr(self, 'city_map') and self.city_map:
                    self.city_map.add_particle_emitter(self.engine_smoke_emitter)
            
            health_ratio = self.health / (self.max_health * 0.6) # 1.0 to 0.0
            smoke_chance = 1.0 - health_ratio
            
            if self.health <= 0:
                base_prob = 100.0 
                bursts = random.randint(3, 6)
            else:
                base_prob = smoke_chance * 50.0 
                bursts = random.randint(1, 3 + int(smoke_chance * 3))
            
            if random.random() < base_prob * dt:
                front_x = self.x + math.cos(self.angle) * 15
                front_y = self.y + math.sin(self.angle) * 15
                
                # Darker smoke when health is very low
                if smoke_chance > 0.8 or self.health <= 0:
                    colors = [(30, 30, 30, 220), (50, 50, 50, 180), (80, 80, 80, 100)]
                else:
                    colors = [(80, 80, 80, 200), (120, 120, 120, 150), (160, 160, 160, 100)]
                
                self.engine_smoke_emitter._spawn_burst(bursts, front_x, front_y, colors)

        # Update engine sounds
        if hasattr(self, 'engine_channels') and self.engine_channels:
            speed_ratio = abs(getattr(self, 'speed', 0)) / max(1, getattr(self, 'max_speed', 1))
            speed_ratio = min(1.0, max(0.0, speed_ratio))
            
            base_vol = 0.2 # Maximum general volume
            
            if self.is_crashed:
                for ch in self.engine_channels.values():
                    if ch: ch.set_volume(0.0)
            else:
                is_damaged = self.health <= 40
                idle_key = "idle_damaged" if is_damaged else "idle_normal"
                other_idle_key = "idle_normal" if is_damaged else "idle_damaged"
                
                v_idle = 0.0
                v_eng1 = 0.0
                v_eng2 = 0.0
                
                if speed_ratio < 0.3:
                    t = speed_ratio / 0.3
                    v_idle = 1.0 - t
                    v_eng1 = t
                elif speed_ratio < 0.8:
                    v_eng1 = 1.0
                else:
                    t = (speed_ratio - 0.8) / 0.2
                    v_eng1 = 1.0 - t
                    v_eng2 = t
                    
                if self.engine_channels.get(idle_key):
                    self.engine_channels[idle_key].set_volume(v_idle * base_vol)
                if self.engine_channels.get(other_idle_key):
                    self.engine_channels[other_idle_key].set_volume(0.0)
                    
                if self.engine_channels.get("engine1"):
                    self.engine_channels["engine1"].set_volume(v_eng1 * base_vol)
                if self.engine_channels.get("engine2"):
                    self.engine_channels["engine2"].set_volume(v_eng2 * base_vol)
                    
                if getattr(self, "is_drifting", False) and abs(getattr(self, 'speed', 0)) > 30:
                    if self.engine_channels.get("drifting"):
                        self.engine_channels["drifting"].set_volume(0.2)
                else:
                    if self.engine_channels.get("drifting"):
                        self.engine_channels["drifting"].set_volume(0.0)

    def init_sounds(self):
        import settings
        self.engine_channels = {}
        for key in ["idle_normal", "idle_damaged", "engine1", "engine2", "drifting"]:
            sound = settings.SOUNDS.get(key)
            if sound:
                channel = sound.play(loops=-1)
                if channel:
                    channel.set_volume(0.0)
                    self.engine_channels[key] = channel

    def stop_sounds(self):
        if hasattr(self, 'engine_channels') and self.engine_channels:
            for ch in self.engine_channels.values():
                if ch:
                    ch.stop()
            self.engine_channels = {}

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not self.is_crashed:
            self.command_bindings.dispatch(self, input_id, input_data)