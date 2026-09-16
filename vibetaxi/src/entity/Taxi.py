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

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id == "toggle_vibe" and input_data.pressed:
            if isinstance(self.state_machine.current, TaxiVibeState):
                self.state_machine.change('idle') 
                print("Exit Vibe")
                
            else:
                self.state_machine.change('vibe')
                print("Enter Vibe")

        if self.state_machine.current:
            self.state_machine.current.on_input(input_id, input_data)