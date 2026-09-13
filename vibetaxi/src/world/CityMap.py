import pygame
import math
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
            tile_index = obj.properties.get("tile_index")
            
            if tile_index in PROPS_DEF:
                definition = PROPS_DEF[tile_index]
                center_x = obj.x + obj.width / 2
                center_y = obj.y + obj.height / 2
                
                prop = Prop(center_x, center_y, definition)
                self.props.append(prop)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.tilemap.pixel_width, self.tilemap.pixel_height)

    def update(self, dt: float) -> None:
        pass

    def render_layers(self, surface: pygame.Surface, camera: Any = None, layer_names: list = None) -> None:
        """Dibuja únicamente las capas especificadas en la lista proporcionada."""
        target_layers = layer_names or []
        for name in target_layers:
            self._render_single_layer(surface, camera, name)
            

    def _render_single_layer(self, surface: pygame.Surface, camera: Any, name: str) -> None:
        grid = self.tilemap.get_layer(name)
        row_range, col_range = (
            range(self.tilemap.rows), range(self.tilemap.cols)
        ) if camera is None else self.tilemap._visible_range(camera)

        for row in row_range:
            for col in col_range:
                gid = grid[row][col]
                if gid == 0:
                    continue
                tileset = self.tilemap.tileset_for_gid(gid)
                if tileset is None:
                    continue
                source_rect = tileset.rect_for(gid)
                x, y = self.tilemap.position_of(row, col)

                if camera is None:
                    surface.blit(tileset.image, (x, y), source_rect)
                else:
                    dest_rect = camera.apply(
                        pygame.Rect(x, y, self.tilemap.tile_width, self.tilemap.tile_height)
                    )
                    surface.blit(tileset.image, dest_rect, source_rect)

    def render_car_silhouette_if_obstructed(self, surface: pygame.Surface, car, camera: Any = None) -> None:
        rect = car.get_collision_rect()
        
        is_covered = False
        min_row = max(0, int(rect.top // self.tilemap.tile_height))
        min_col = max(0, int(rect.left // self.tilemap.tile_width))
        max_row = min(self.tilemap.rows - 1, int((rect.bottom - 1) // self.tilemap.tile_height))
        max_col = min(self.tilemap.cols - 1, int((rect.right - 1) // self.tilemap.tile_width))

        for name in settings.TILED_UPPER_LAYERS:
            if name not in self.tilemap.layer_names():
                continue
            grid = self.tilemap.get_layer(name)
            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    if grid[row][col] != 0:
                        is_covered = True
                        break
                if is_covered:
                    break
            if is_covered:
                break

        if not is_covered:
            return

        texture = settings.TEXTURES[car.texture_id]
        frame = settings.FRAMES[car.texture_id][car.frame_index]
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.fill((0, 0, 0, 0))
        image.blit(texture, (0, 0), frame)

        angle = getattr(car, "angle", None)
        if angle is not None:
            angle_offset = getattr(car, "angle_offset", 0)
            degrees = math.degrees(-angle) + angle_offset
            image = pygame.transform.rotate(image, degrees)

        mask = pygame.mask.from_surface(image)
        silhouette = mask.to_surface(setcolor=(0, 0, 0, 160), unsetcolor=(0, 0, 0, 0))

        sil_rect = silhouette.get_rect(center=(car.x, car.y))
        if camera is not None:
            sil_rect = camera.apply(sil_rect)

        surface.blit(silhouette, sil_rect)