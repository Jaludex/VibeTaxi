import pygame
import settings
import random
from gale.input_handler import InputData
from gale.timer import Timer
from gale.text import render_text

class Radio:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
        self.volumen = 50
        self.songs = ["rock", "pop", "hiphop", "electronic"]
        self.ind_song = 1
        self.angulo_perilla = [45, 0, -45, -90]
        self.pos_marker_list = [self.x + 100, self.x + 125, self.x + 175, self.x + 325]
        
        self.estado_plus = 0  # 0 = Normal, 1 = Presionado
        self.estado_less = 0 
        self.timer_plus = 0.0
        self.timer_less = 0.0
        self.tiempo_animacion = 0.15
        
        self.pos_centro_perilla = (self.x + 36, self.y + 31) 
        self.pos_btn_plus = (self.x + 422, self.y + 7)
        self.pos_btn_less = (self.x + 421, self.y + 32)
        self.pos_marker_x, self.pos_marker_y = self.x + 100, self.y + 24
        
    def generate_num_random(self, lenn: int) -> int:
        return random.randint(1, lenn)

    def update(self, dt: float):
        if self.estado_plus == 1:
            self.timer_plus -= dt
            if self.timer_plus <= 0:
                self.estado_plus = 0
                
        if self.estado_less == 1:
            self.timer_less -= dt
            if self.timer_less <= 0:
                self.estado_less = 0
        
    def get_current_song(self) -> str:
        return self.songs[self.ind_song]

    def render(self, surface):
        # 1. Base consumida del diccionario global TEXTURES
        surface.blit(settings.TEXTURES["radio"], (self.x, self.y))
        surface.blit(settings.TEXTURES["marker"], (self.pos_marker_x, self.pos_marker_y))
        
        # 2. Perilla rotada
        angulo = self.angulo_perilla[self.ind_song]
        perilla_rotada = pygame.transform.rotate(settings.TEXTURES["button-radio"], angulo)
        rect_perilla = perilla_rotada.get_rect(center=self.pos_centro_perilla)
        surface.blit(perilla_rotada, rect_perilla.topleft)
        
        # 3. Botones consumidos del diccionario global FRAMES
        surface.blit(settings.TEXTURES["button-plus"], self.pos_btn_plus, settings.FRAMES["button-plus"][self.estado_plus])
        surface.blit(settings.TEXTURES["button-less"], self.pos_btn_less, settings.FRAMES["button-less"][self.estado_less])
        
        render_text(
            surface,
            f"{self.songs[self.ind_song]}",
            settings.FONTS["minecraft"],
            self.x + 240,
            self.y + 5,
            (0, 0, 0),
            center=True
        )
        
        

    def on_input(self, input_id: str, input_data: InputData):
        if input_data.pressed:
            if input_id == "vol-up" and input_data.pressed:
                self.volumen = min(100, self.volumen + 10)
                self.estado_plus = 1
                self.timer_plus = self.tiempo_animacion
                pygame.mixer.music.set_volume(self.volumen / 100.0)
                
            elif input_id == "vol-down":
                self.volumen = max(0, self.volumen - 10)
                self.estado_less = 1
                self.timer_less = self.tiempo_animacion
                pygame.mixer.music.set_volume(self.volumen / 100.0)
                
            elif input_id == "next-song":
                self.ind_song = (self.ind_song + 1) % settings.CANT_MUSIC_CHANNELS
                Timer.tween(
                    0.15, 
                    [(self, {"pos_marker_x": self.pos_marker_list[self.ind_song]})],
                    on_finish=None
                )
                if self.ind_song == 0:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_ROCK[f"rock-{self.generate_num_random(len(settings.MUSIC_ROCK))}"])
                    pygame.mixer.music.play(-1)
                if self.ind_song == 1:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_POP[f"pop-{self.generate_num_random(len(settings.MUSIC_POP))}"])
                    pygame.mixer.music.play(-1)
                if self.ind_song == 2:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_HIPHOP[f"hiphop-{self.generate_num_random(len(settings.MUSIC_HIPHOP))}"])
                    pygame.mixer.music.play(-1)
                if self.ind_song == 3:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_ELECTRONIC[f"electronic-{self.generate_num_random(len(settings.MUSIC_ELECTRONIC))}"])
                    pygame.mixer.music.play(-1)
                
                
            elif input_id == "prev-song":
                self.ind_song = (self.ind_song - 1) % settings.CANT_MUSIC_CHANNELS
                Timer.tween(
                    0.15, 
                    [(self, {"pos_marker_x": self.pos_marker_list[self.ind_song]})],
                    on_finish=None
                )
                if self.ind_song == 0:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_ROCK[f"rock-{self.generate_num_random(len(settings.MUSIC_ROCK))}"])
                    pygame.mixer.music.play(-1)
                if self.ind_song == 1:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_POP[f"pop-{self.generate_num_random(len(settings.MUSIC_POP))}"])
                    pygame.mixer.music.play(-1)
                if self.ind_song == 2:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_HIPHOP[f"hiphop-{self.generate_num_random(len(settings.MUSIC_HIPHOP))}"])
                    pygame.mixer.music.play(-1)
                if self.ind_song == 3:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(settings.MUSIC_ELECTRONIC[f"electronic-{self.generate_num_random(len(settings.MUSIC_ELECTRONIC))}"])
                    pygame.mixer.music.play(-1)
    