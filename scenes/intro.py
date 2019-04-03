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
        boot_text = [
            "1 0 0x000A4 0x00000000000000000 start memoty discovery 0 0x0000A4",
            "0x00000000000000000 1 0 0x000014 0 0x00000000000000000 CPUO starting cell",
            "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009",
            "0x00000000000000000 CPUD launch EFI0 0x0000A4 0x00000000000000000 1 0",
            "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4",
            "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory",
            "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000",
            "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014",
            "0x00000000000000000 CPUO stating cell relocation0 0x0000A4",
            "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0",
            "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO",
            "stating EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4",
            "0x00000000000000000 start memory discovery 0 0x0000A4 0x00000000000000000"]

        self.loader_text = [
            "*************** PIP-OS(R) V7.1.08 ***************",
            "",
            "",
            "",
            "COPYRIGHT 2075 ROBCO(R)",
            "LOADER V1.1",
            "EXEC VERSION 41.10",
            "64k RAM SYSTEM",
            "38911 BYTES FREE",
            "NO HOLOTAPE FOUND",
            "LOAD ROM(1): DEITRIX 303"]

        for i in range(0, 8):
            for t in boot_text:
                text.append(t)
        text[0] = "* " + text[0]

        font = pg.font.Font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'monofonto.ttf'), 8)
        font_size = font.size(' ')
        surf_size = (font_size[0] * 73, font_size[1] * 104)
        self.surface = pg.Surface(surf_size)

        for idx, t in enumerate(text):
            text_s = font.render(t, True, (255,255,255))
            self.surface.blit(text_s, (0, int(idx * font_size[1])))

        self.velocity = surf_size[1] / 2
        self.text_y = cfg.height

        self.fontX2 = pg.font.Font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'monofonto.ttf'), 16)
        font_size = self.fontX2.size(' ')
        surf_size = (font_size[0] * 73, font_size[1] * 104)
        self.cursor_rect = pg.Rect((0,0), font_size);
        self.surface_loader = pg.Surface((font_size[0] * 49, font_size[1] * len(self.loader_text)))
        self.cursor_show = True
        self.cursor_cd = 0
        self.loader_y = 0
        self.typing_cd = 0
        self.loader_text = "\n".join(self.loader_text)

        self.state = 0
        pg.time.delay(1000)
        self.text_pos = [0, 0, 0]
        self.typing_time = 0.1
        self.state2_cd = 0
        self.cursor_rect_extra = [0, 0]

    def process_input(self, events, keys):
        pass

    def roll_text(self, dt):
        if self.text_y < ((self.surface.get_height())*-1):
            self.state = 1
            pg.time.delay(500)
        else:
            self.text_y -= self.velocity * dt
        pass

    def loader_sequence(self, dt):
        if self.typing_cd >= self.typing_time :
            c = self.loader_text[self.text_pos[2]]
            if c == "\n":
                self.text_pos[1] += 1
                self.text_pos[0] = 0
                self.typing_time = 0.2
            else:
                text_s = self.fontX2.render(c, True, (255, 255, 255))
                text_size = self.fontX2.size(' ')
                self.surface_loader.blit(text_s, (text_size[0] * self.text_pos[0], text_size[1] * self.text_pos[1]))
                self.cursor_rect_extra = (text_size[1] * self.text_pos[1], text_size[0] * (self.text_pos[0]+1))
                self.text_pos[0] += 1
                self.typing_time = 0.02
            self.text_pos[2] += 1
            self.typing_cd = 0

        self.typing_cd += dt
        if self.text_pos[2] >= len(self.loader_text):
            self.state = 2

    def blink_cursor(self, dt):
        if self.cursor_cd >= 0.6:
            self.cursor_cd = 0
            self.cursor_show = not self.cursor_show
        self.cursor_cd += dt

    def update(self, dt):
        if self.state == 0:
            self.roll_text(dt)
        elif self.state == 1:
            self.blink_cursor(dt)
            self.loader_sequence(dt)
        elif self.state == 2:
            if self.state2_cd >= 3:
                self.state = 3
            self.blink_cursor(dt)
            self.state2_cd += dt
        pass

    def render(self, render):
        if self.state == 0:
            render.blit(self.surface, (cfg.width / 2 - self.surface.get_width()/2, self.text_y))
        if self.state == 1 or self.state == 2:
            render.blit(self.surface_loader, (cfg.width / 2 - self.surface_loader.get_width()/2, (cfg.height/2 - self.surface_loader.get_height() / 2) + self.loader_y) )
            if self.cursor_show:
                self.cursor_rect.left = (cfg.width/2 - self.surface_loader.get_width()/2) + self.cursor_rect_extra[1]
                self.cursor_rect.top = (cfg.height/2 - self.surface_loader.get_height() / 2) + self.loader_y + self.cursor_rect_extra[0]
                pg.draw.rect(render, (255, 255, 255), self.cursor_rect)
        pass
