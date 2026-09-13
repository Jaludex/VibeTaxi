import pygame
from typing import Any
from gale.tilemap import load_tiled_map
import settings

class CityMap:
    def __init__(self, map_key: str = "city") -> None:
        # Carga el mapa usando la llave proporcionada
        self.tilemap = load_tiled_map(settings.TILEMAPS[map_key])

    def get_rect(self) -> pygame.Rect:
        # Devuelve las dimensiones totales del mapa para los límites de la cámara
        return pygame.Rect(0, 0, self.tilemap.pixel_width, self.tilemap.pixel_height)

    def update(self, dt: float) -> None:
        # Espacio reservado para actualizar animaciones de tiles, semáforos o tráfico futuro
        pass

    def render(self, surface: pygame.Surface, camera: Any) -> None:
        # Gale renderiza automáticamente las capas del tilemap usando la cámara
        self.tilemap.render(surface, camera)