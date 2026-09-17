import pygame
import random
import settings
from gale.input_handler import InputData
from gale.timer import Timer
from gale.text import render_text
from src.definitions.radio import RADIO_STATIONS

class Radio:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
        self.volumen = 50
        self.stations = RADIO_STATIONS
        self.songs = [station["name"] for station in self.stations]
        self.ind_song = 0
        
        self.estado_plus = 0  # 0 = Normal, 1 = Presionado
        self.estado_less = 0 
        self.tiempo_animacion = 0.15
        
        self.pos_centro_perilla = (self.x + 36, self.y + 31) 
        self.pos_btn_plus = (self.x + 422, self.y + 7)
        self.pos_btn_less = (self.x + 421, self.y + 32)
        
        self.pos_marker_x, self.pos_marker_y = self.get_marker_x(self.ind_song), self.y + 24
        self.knob_angle = self.get_knob_angle(self.ind_song)
        
        self.alpha = 0.0
        
        self._fade_out_timer = None
        self._alpha_tween = None
        self._plus_timer = None
        self._less_timer = None

        from gale.command import CommandBindings
        from src import commands

        self.command_bindings = CommandBindings()
        self.command_bindings.bind("vol-up", press=commands.RADIO_VOL_UP)
        self.command_bindings.bind("vol-down", press=commands.RADIO_VOL_DOWN)
        self.command_bindings.bind("next-song", press=commands.RADIO_NEXT_STATION)
        self.command_bindings.bind("prev-song", press=commands.RADIO_PREV_STATION)
        
    def get_marker_x(self, index: int) -> float:
        origin_x = self.x + 80
        width = 302
        if len(self.stations) <= 1:
            return origin_x
        return origin_x + (index / (len(self.stations) - 1)) * width

    def get_knob_angle(self, index: int) -> float:
        if len(self.stations) <= 1:
            return 90
        return 90 - (index / (len(self.stations) - 1)) * 180

    def update(self, dt: float):
        station = self.stations[self.ind_song]
        # Si la emisora tiene música y la música se detuvo (terminó la canción)
        if station["songs"] and not pygame.mixer.music.get_busy():
            song = random.choice(station["songs"])
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(0) # Reproducir sin bucles desde el inicio
            
    def get_current_song(self) -> str:
        return self.songs[self.ind_song]

    def get_current_genre(self) -> str:
        return self.stations[self.ind_song].get("genre")

    def render(self, surface):
        if self.alpha <= 0:
            return
            
        radio_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        
        radio_surf.blit(settings.TEXTURES["radio"], (self.x, self.y))
        radio_surf.blit(settings.TEXTURES["marker"], (self.pos_marker_x, self.pos_marker_y))
        
        angulo = self.knob_angle
        perilla_rotada = pygame.transform.rotate(settings.TEXTURES["button-radio"], angulo)
        rect_perilla = perilla_rotada.get_rect(center=self.pos_centro_perilla)
        radio_surf.blit(perilla_rotada, rect_perilla.topleft)
        
        radio_surf.blit(settings.TEXTURES["button-plus"], self.pos_btn_plus, settings.FRAMES["button-plus"][self.estado_plus])
        radio_surf.blit(settings.TEXTURES["button-less"], self.pos_btn_less, settings.FRAMES["button-less"][self.estado_less])
        
        render_text(
            radio_surf,
            f"{self.songs[self.ind_song]}",
            settings.FONTS["minecraft"],
            self.x + 240,
            self.y + 8,
            (0, 0, 0),
            center=True
        )
        
        radio_surf.set_alpha(int(self.alpha))
        surface.blit(radio_surf, (0, 0))

    def change_station(self):
        Timer.tween(
            0.15, 
            [(self, {
                "pos_marker_x": self.get_marker_x(self.ind_song),
                "knob_angle": self.get_knob_angle(self.ind_song)
            })],
            on_finish=None
        )
        
        pygame.mixer.music.stop()
        station = self.stations[self.ind_song]
        if station["songs"]:
            song = random.choice(station["songs"])
            start_time = random.uniform(0.0, 60.0)
            pygame.mixer.music.load(song)
            try:
                # Reproducir una vez (0 bucles) con salto de tiempo
                pygame.mixer.music.play(0, start=start_time)
            except Exception:
                pygame.mixer.music.play(0)

    def _start_fade_out(self):
        if self._alpha_tween:
            self._alpha_tween.remove()
        self._alpha_tween = Timer.tween(1.0, [(self, {"alpha": 0.0})])

    def _trigger_ui_activity(self):
        if self._fade_out_timer:
            self._fade_out_timer.remove()
        if self._alpha_tween:
            self._alpha_tween.remove()
        
        self.alpha = 255.0
        self._fade_out_timer = Timer.after(settings.RADIO_FADEOUT_TIME, self._start_fade_out)

    def volume_up(self):
        self._trigger_ui_activity()
        self.volumen = min(100, self.volumen + 10)
        self.estado_plus = 1
        if self._plus_timer:
            self._plus_timer.remove()
        self._plus_timer = Timer.after(self.tiempo_animacion, lambda: setattr(self, 'estado_plus', 0))
        pygame.mixer.music.set_volume(self.volumen / 100.0)

    def volume_down(self):
        self._trigger_ui_activity()
        self.volumen = max(0, self.volumen - 10)
        self.estado_less = 1
        if self._less_timer:
            self._less_timer.remove()
        self._less_timer = Timer.after(self.tiempo_animacion, lambda: setattr(self, 'estado_less', 0))
        pygame.mixer.music.set_volume(self.volumen / 100.0)

    def next_station(self):
        self._trigger_ui_activity()
        self.ind_song = (self.ind_song + 1) % len(self.stations)
        self.change_station()

    def prev_station(self):
        self._trigger_ui_activity()
        self.ind_song = (self.ind_song - 1) % len(self.stations)
        self.change_station()

    def on_input(self, input_id: str, input_data: InputData):
        self.command_bindings.dispatch(self, input_id, input_data)