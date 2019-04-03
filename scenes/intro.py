from .scene_base import SceneBase
import pygame as pg
import config as cfg
import os, json

class IntroScene(SceneBase):

    def __init__(self):
        super().__init__()
        #o texto de código deve se repitir 8 vezes e deve passar na tela na duração de 4 segundos
        text = []
        text_size = [0, 0]
        with open(os.path.join(cfg.data_folder, "intro_text.json")) as json_file:
            data = json.load(json_file)
            for i in range(1, 8):
                for t in data['boot']:
                    text_size[0] += 1
                    if len(t) > text_size[1]:
                        text_size[1] = len(t)
                    text.append(t)
        text[0] = "* " + text[0]
        font = pg.font.Font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'monofonto.ttf'), 8)
        font_size = font.size(' ')
        surf_size = (font_size[0] * text_size[0], font_size[1] * text_size[1])
        self.surface = pg.Surface(surf_size)
        for idx, t in enumerate(text):
            text_s = font.render(t, True, (255,255,255))
            self.surface.blit(text_s, (0, int(idx * font_size[1])))
        self.velocity = surf_size[1] / 2
        self.text_y = cfg.height
        self.state = 0
        pg.time.delay(1000)
        pass

    def process_input(self, events, keys):
        pass

    def roll_text(self, dt):
        if self.text_y < ((self.surface.get_height())*-1):
            self.state = 1
        else:
            self.text_y -= self.velocity * dt
        pass

    def update(self, dt):
        if self.state == 0:
            self.roll_text(dt)

    def render(self, render):
        if self.state == 0:
            render.blit(self.surface, (cfg.width / 2 - self.surface.get_width()/3, self.text_y))
        pass
