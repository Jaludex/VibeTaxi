import pygame
from typing import Any, List
from gale.tilemap import load_tiled_map
import settings
from src.entity.Prop import Prop
from src.definitions.props import PROPS_DEF

class CityMap:
    def __init__(self, map_key: str = "city") -> None:
        self.tilemap = load_tiled_map(settings.TILEMAPS[map_key])
        self.props: List[Prop] = []
        
        self._load_props()

    def _load_props(self) -> None:
        for obj in self.tilemap.object_layers.get("props", []):
            tile_index = obj.properties.get("tile_index", None)
            
            if tile_index in PROPS_DEF:
                definition = PROPS_DEF[tile_index]
                prop = Prop(obj.x, obj.y, definition)
                self.props.append(prop)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.tilemap.pixel_width, self.tilemap.pixel_height)

    def update(self, dt: float) -> None:
        for prop in self.props:
            prop.update(dt)
            
        self.props = [p for p in self.props if p.active]

    def render(self, surface: pygame.Surface, camera: Any) -> None:
        self.tilemap.render(surface, camera)
        
        for prop in self.props:
            prop.render(surface, camera)