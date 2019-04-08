import pygame as pg
import fonts

class Header(pg.sprite.DirtySprite):
    def __init__(self, rect, color=(255,255,255), selected_index=0):
        pg.sprite.DirtySprite.__init__(self)
        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.rect = rect
        self.texts = { "STAT": 0, "INV":0, "DATA":0, "MAP":0, "RADIO":0 }
        self.color = color
        self.selected_index = selected_index
        self.draw_header()

    def draw_header(self):
        margin = 56
        pg.draw.lines(self.image, self.color, False, [
            (margin, self.rect.height),
            (margin, self.rect.height-8),
            (self.rect.width - margin, self.rect.height-8),
            (self.rect.width - margin, self.rect.height),
            ], 2)
        selected_item = list(self.texts)[self.selected_index]
        font = fonts.MONOFONTO_18
        font.set_bold(True)
        for name, position in self.texts.items():
            text_sur = font.render(name, True, self.color)
            if selected_item == name:
                t = pg.Surface((text_sur.get_width(), text_sur.get_height()+10))
                t.fill((0,0,0))
                t.blit(text_sur, (0, 0))
                text_sur = t
            self.image.blit(text_sur, (position, 10))
        self.dirty = 1

    def update(self, dt):
        self.dirty = 1
