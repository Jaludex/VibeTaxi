from typing import Any, List, Optional
import pygame
from gale.particle_system import ParticleSystem
from gale.timer import Timer


class ParticleEmitter:
    def __init__(
        self,
        x: float,
        y: float,
        colors: List[Any],
        emission_duration: float = 0.0,
        emission_interval: float = 0.08,
        particles_per_burst: int = 4,
        single_burst_count: int = 15,
        lifetime_min: float = 0.2,
        lifetime_max: float = 0.5,
        accel: float = 2.0,
        spread: float = 4.0,
        particle_size: int = 4,
        is_ground: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.colors = colors
        self.emission_duration = emission_duration
        self.emission_interval = emission_interval
        self.particles_per_burst = particles_per_burst
        self.single_burst_count = single_burst_count
        self.lifetime_min = lifetime_min
        self.lifetime_max = lifetime_max
        self.accel = accel
        self.spread = spread
        self.particle_size = particle_size
        self.is_ground = is_ground

        self.systems: List[ParticleSystem] = []
        self._is_emitting: bool = True
        self._timer_item: Optional[Any] = None

        # Ráfaga inicial inmediata
        initial_count = (
            self.single_burst_count
            if self.emission_duration <= 0
            else self.particles_per_burst
        )
        self._spawn_burst(initial_count)

        # Si la emisión es continua en el tiempo, delegamos el intervalo a gale.timer.Timer.every
        if self.emission_duration > 0 and self.emission_interval > 0:
            burst_limit = max(1, int(self.emission_duration / self.emission_interval))
            self._timer_item = Timer.every(
                self.emission_interval,
                lambda: self._spawn_burst(self.particles_per_burst),
                limit=burst_limit,
                on_finish=self._stop_emission,
            )
        else:
            self._is_emitting = False

    def _spawn_burst(self, count: int) -> None:
        ps = ParticleSystem(self.x, self.y, n=count)
        ps.set_life_time(self.lifetime_min, self.lifetime_max)
        ps.set_linear_acceleration(-self.accel, -self.accel, self.accel, self.accel)
        ps.set_area_spread(self.spread, self.spread)
        ps.set_colors(self.colors)
        ps.generate()
        self.systems.append(ps)

    def _stop_emission(self) -> None:
        self._is_emitting = False
        self._timer_item = None

    def stop(self) -> None:
        """Cancela la emisión programada inmediatamente."""
        if self._timer_item is not None:
            self._timer_item.remove()
            self._timer_item = None
        self._is_emitting = False

    def is_finished(self) -> bool:
        return not self._is_emitting and len(self.systems) == 0

    def update(self, dt: float) -> None:
        # Solo actualiza la física y vida de las partículas activas
        for ps in self.systems:
            ps.update(dt)

        self.systems = [ps for ps in self.systems if len(ps.particles) > 0]

    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        size = self.particle_size
        half_size = max(1, size // 2)
        for ps in self.systems:
            for p in ps.particles:
                if ps.timer < p.life_time:
                    if camera is not None:
                        rect = camera.apply(pygame.Rect(int(p.x), int(p.y), size, size))
                    else:
                        rect = pygame.Rect(int(p.x), int(p.y), size, size)

                    s = pygame.Surface((size, size), pygame.SRCALPHA)
                    alpha = p.color[3] if len(p.color) >= 4 else 255
                    color = (p.color[0], p.color[1], p.color[2], alpha)
                    pygame.draw.circle(s, color, (half_size, half_size), half_size)
                    surface.blit(s, rect)

    @classmethod
    def create_sparks(
        cls, x: float, y: float, count: int = 12
    ) -> "ParticleEmitter":
        """Generates a burst of bright sparks (yellow/orange/white) for metal impacts."""
        spark_colors = [
            (255, 255, 200, 255),
            (255, 220, 50, 255),
            (255, 140, 0, 255),
            (255, 255, 255, 255),
        ]
        return cls(
            x,
            y,
            colors=spark_colors,
            emission_duration=0.0,
            single_burst_count=count,
            lifetime_min=0.1,
            lifetime_max=0.3,
            accel=3.0,
            spread=3.0,
            particle_size=3,
        )

    @classmethod
    def create_smoke(
        cls, x: float, y: float, duration: float = 1.0
    ) -> "ParticleEmitter":
        """Generates sustained smoke/dust for scraping or hard collisions."""
        smoke_colors = [
            (200, 200, 200, 180),
            (160, 160, 160, 140),
            (120, 120, 120, 100),
        ]
        return cls(
            x,
            y,
            colors=smoke_colors,
            emission_duration=duration,
            emission_interval=0.06,
            particles_per_burst=3,
            lifetime_min=0.2,
            lifetime_max=0.5,
            accel=1.5,
            spread=5.0,
            particle_size=4,
        )

    @classmethod
    def create_drift_smoke(
        cls, x: float, y: float, count: int = 2
    ) -> "ParticleEmitter":
        """Generates a soft puff of tire smoke when drifting."""
        smoke_colors = [
            (240, 240, 240, 150),
            (215, 215, 215, 120),
            (190, 190, 190, 80),
            (255, 255, 255, 140),
        ]
        return cls(
            x,
            y,
            colors=smoke_colors,
            emission_duration=0.0,
            single_burst_count=count,
            lifetime_min=0.25,
            lifetime_max=0.5,
            accel=1.0,
            spread=2.0,
            particle_size=4,
            is_ground=False,
        )

    @classmethod
    def create_skid_mark(
        cls, x: float, y: float, lifetime: float = 2.5
    ) -> "ParticleEmitter":
        """Generates an immobile, static dark tire mark on the ground using particles."""
        return cls(
            x,
            y,
            colors=[(35, 35, 35, 140)],
            emission_duration=0.0,
            single_burst_count=1,
            lifetime_min=lifetime,
            lifetime_max=lifetime,
            accel=0.0,
            spread=0.0,
            particle_size=4,
            is_ground=True,
        )


