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
        
        self.volume = 50
        self.stations = RADIO_STATIONS
        self.songs = [station["name"] for station in self.stations]
        self.ind_song = 0
        
        self.state_plus = 0  # 0 = Normal, 1 = Pressed
        self.state_less = 0 
        self.animation_time = 0.15
        
        self.knob_center_pos = (self.x + 36, self.y + 31) 
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
        # If the station has music and the music stopped (song finished)
        if station["songs"] and not pygame.mixer.music.get_busy():
            song = random.choice(station["songs"])
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(0) # Play without loops from the start
            
    def get_current_song(self) -> str:
        return self.songs[self.ind_song]

    def get_current_genre(self) -> str:
        return self.stations[self.ind_song].get("genre")

    def render(self, surface):
        if self.alpha <= 0:
            return

        rad_tex = settings.TEXTURES.get("radio")
        if not rad_tex:
            return
        rw, rh = rad_tex.get_size()

        # If fully opaque, blit directly to target surface for max performance.
        # Otherwise, render onto a radio-sized buffer (480x64) with uniform alpha.
        if self.alpha >= 254.0:
            target_surf = surface
            ox, oy = int(self.x), int(self.y)
        else:
            if not hasattr(self, "_radio_buf") or self._radio_buf.get_size() != (rw, rh):
                self._radio_buf = pygame.Surface((rw, rh)).convert()
            target_surf = self._radio_buf
            ox, oy = 0, 0

        target_surf.blit(rad_tex, (ox, oy))
        target_surf.blit(settings.TEXTURES["marker"], (ox + int(self.pos_marker_x - self.x), oy + 24))

        angle = round(self.knob_angle, 1)
        if not hasattr(self, "_knob_cache"):
            self._knob_cache = {}
        knob_surf = self._knob_cache.get(angle)
        if knob_surf is None:
            knob_surf = pygame.transform.rotate(settings.TEXTURES["button-radio"], angle)
            if len(self._knob_cache) < 40:
                self._knob_cache[angle] = knob_surf
        knob_rect = knob_surf.get_rect(center=(ox + 36, oy + 31))
        target_surf.blit(knob_surf, knob_rect.topleft)

        target_surf.blit(settings.TEXTURES["button-plus"], (ox + 422, oy + 7), settings.FRAMES["button-plus"][self.state_plus])
        target_surf.blit(settings.TEXTURES["button-less"], (ox + 421, oy + 32), settings.FRAMES["button-less"][self.state_less])

        curr_song = self.songs[self.ind_song]
        if not hasattr(self, "_cached_txts"):
            self._cached_txts = {}
        txt_surf = self._cached_txts.get(curr_song)
        if txt_surf is None:
            txt_surf = settings.FONTS["minecraft"].render(curr_song, True, (0, 0, 0))
            self._cached_txts[curr_song] = txt_surf
        rect = txt_surf.get_rect(center=(ox + 240, oy + 6))
        target_surf.blit(txt_surf, rect)

        if self.alpha < 254.0:
            self._radio_buf.set_alpha(int(self.alpha))
            surface.blit(self._radio_buf, (int(self.x), int(self.y)))

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
            from src.os_tools import is_android
            song = random.choice(station["songs"])
            pygame.mixer.music.load(song)
            if is_android():
                # On Android, avoid synchronous MP3 seek which freezes the main thread by ~500ms
                pygame.mixer.music.play(0)
            else:
                try:
                    start_time = random.uniform(0.0, 60.0)
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
        from src import audio
        audio.play_sfx("press")
        self._trigger_ui_activity()
        self.volume = min(100, self.volume + 10)
        self.state_plus = 1
        if self._plus_timer:
            self._plus_timer.remove()
        self._plus_timer = Timer.after(self.animation_time, lambda: setattr(self, 'state_plus', 0))
        audio.set_music_volume(self.volume / 100.0)

    def volume_down(self):
        from src import audio
        audio.play_sfx("press")
        self._trigger_ui_activity()
        self.volume = max(0, self.volume - 10)
        self.state_less = 1
        if self._less_timer:
            self._less_timer.remove()
        self._less_timer = Timer.after(self.animation_time, lambda: setattr(self, 'state_less', 0))
        audio.set_music_volume(self.volume / 100.0)

    def next_station(self):
        from src import audio
        audio.play_sfx("press")
        self._trigger_ui_activity()
        self.ind_song = (self.ind_song + 1) % len(self.stations)
        self.change_station()

    def prev_station(self):
        from src import audio
        audio.play_sfx("press")
        self._trigger_ui_activity()
        self.ind_song = (self.ind_song - 1) % len(self.stations)
        self.change_station()

    def on_input(self, input_id: str, input_data: InputData):
        self.command_bindings.dispatch(self, input_id, input_data)