import math
from src.states.entity.TaxiDriveState import TaxiDriveState
from src import commands

class TaxiVibeState(TaxiDriveState):
    def enter(self, **kwargs):
        # 1. Guardamos valores originales
        self.original_max_speed = self.entity.max_speed
        self.original_turn_speed = self.entity.turn_speed

        self.entity.max_speed *= 1.4  
        self.entity.is_drifting = False

        self.slide_vx = self.entity.vx
        self.slide_vy = self.entity.vy
        
        super().enter(**kwargs)

    def exit(self):
        self.entity.max_speed = self.original_max_speed
        self.entity.turn_speed = self.original_turn_speed
        self.entity.is_drifting = False
        self._last_wl = None
        self._last_wr = None
        
        if hasattr(self, "_drift_smoke_emitter") and self._drift_smoke_emitter:
            self._drift_smoke_emitter.is_permanent = False
        if hasattr(self, "_skid_mark_emitter") and self._skid_mark_emitter:
            self._skid_mark_emitter.is_permanent = False

    def update(self, dt):
        if getattr(self.entity, "is_drifting", False):
            self.entity.turn_speed = self.original_turn_speed * 2.2
        else:
            self.entity.turn_speed = self.original_turn_speed

        super().update(dt)

        ideal_vx = self.entity.vx
        ideal_vy = self.entity.vy

        if getattr(self.entity, "is_drifting", False):
            grip = 3.5  
        else:
            grip = 12.0 

        self.slide_vx += (ideal_vx - self.slide_vx) * grip * dt
        self.slide_vy += (ideal_vy - self.slide_vy) * grip * dt

        if getattr(self.entity, "is_drifting", False):
            current_speed = math.hypot(self.slide_vx, self.slide_vy)
            ideal_speed = abs(self.entity.speed)
            
            if current_speed > 0.1 and ideal_speed > 0.1:
                ratio = (ideal_speed * 0.95) / current_speed 
                if ratio > 1.0:
                    self.slide_vx *= ratio
                    self.slide_vy *= ratio

        self.entity.vx = self.slide_vx
        self.entity.vy = self.slide_vy

        self._handle_drift_particles(dt)

    def _handle_drift_particles(self, dt: float) -> None:
        if not getattr(self.entity, "is_drifting", False):
            self._last_wl = None
            self._last_wr = None
            return

        current_speed = math.hypot(self.slide_vx, self.slide_vy)
        if current_speed < 30:
            self._last_wl = None
            self._last_wr = None
            return

        city_map = getattr(self.entity, "city_map", None)
        if city_map is None:
            return

        cos_a = math.cos(self.entity.angle)
        sin_a = math.sin(self.entity.angle)
        right_x = -sin_a
        right_y = cos_a

        # Posiciones de los extremos traseros (ruedas traseras)
        x, y = self.entity.x, self.entity.y
        wl_x = x - 10 * cos_a - 5 * right_x
        wl_y = y - 10 * sin_a - 5 * right_y
        wr_x = x - 10 * cos_a + 5 * right_x
        wr_y = y - 10 * sin_a + 5 * right_y

        from src.ParticleEmitter import ParticleEmitter

        # Inicializar emisores únicos si no existen
        if not hasattr(self, "_drift_smoke_emitter") or not self._drift_smoke_emitter:
            self._drift_smoke_emitter = ParticleEmitter.create_drift_smoke(0, 0, count=0)
            self._drift_smoke_emitter.is_permanent = True
            city_map.add_particle_emitter(self._drift_smoke_emitter)
            
        if not hasattr(self, "_skid_mark_emitter") or not self._skid_mark_emitter:
            self._skid_mark_emitter = ParticleEmitter.create_skid_mark(0, 0)
            self._skid_mark_emitter.is_permanent = True
            city_map.add_particle_emitter(self._skid_mark_emitter)

        # 1. Partículas de humo saliendo de las llantas traseras
        if not hasattr(self, "_smoke_timer"):
            self._smoke_timer = 0.0
        self._smoke_timer += dt
        if self._smoke_timer >= 0.06:
            self._smoke_timer = 0.0
            self._drift_smoke_emitter._spawn_burst(2, wl_x, wl_y)
            self._drift_smoke_emitter._spawn_burst(2, wr_x, wr_y)

        # 2. Partículas estáticas como huellas/marcas de neumáticos en el suelo
        last_wl = getattr(self, "_last_wl", None)
        last_wr = getattr(self, "_last_wr", None)

        spawn_skid = False
        if last_wl is None or last_wr is None:
            spawn_skid = True
        else:
            dist_l = math.hypot(wl_x - last_wl[0], wl_y - last_wl[1])
            dist_r = math.hypot(wr_x - last_wr[0], wr_y - last_wr[1])
            if dist_l >= 4.0 or dist_r >= 4.0:
                spawn_skid = True

        if spawn_skid:
            self._skid_mark_emitter._spawn_burst(1, wl_x, wl_y)
            self._skid_mark_emitter._spawn_burst(1, wr_x, wr_y)
            self._last_wl = (wl_x, wl_y)
            self._last_wr = (wr_x, wr_y)