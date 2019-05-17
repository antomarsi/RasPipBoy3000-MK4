import pygame as pg
import fonts


class SubHeader(pg.sprite.DirtySprite):
    def __init__(self, x=0, y=0, color=(255, 255, 255), selected_index=0, texts=["TEXT1", "TEXT2"]):
        pg.sprite.DirtySprite.__init__(self)
        self.texts = texts
        self.color = color
        self.font = fonts.MONOFONTO_16
        self.font.set_bold(True)
        self.selected_index = selected_index
        self.texts_surfaces = []
        self.draw_text_surfaces()
        self.draw_list()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_index_pos(self):
        font_width, font_height = self.font.size(" ")
        pos = 0
        for idx, sur in enumerate(self.texts_surfaces):
            if idx < self.selected_index:
                pos += sur.get_width()
                pos += font_width/2
            else:
                break
        return pos

    def set_index(self, new_index):
        self.selected_index = new_index
        self.draw_text_surfaces()
        self.draw_list()

    def next_index(self):
        self.set_index(max(0, min(self.selected_index+1, len(self.texts)-1)))

    def prev_index(self):
        self.set_index(max(0, min(self.selected_index-1, len(self.texts)-1)))

    def draw_text_surfaces(self):
        self.texts_surfaces.clear()
        for idx, text in enumerate(self.texts):
            division = abs(idx - self.selected_index) + 1
            if (idx < self.selected_index):
                division = 4
            if (division > 2):
                division += 2
            if (division <= 5):
                color = (self.color[0] / division,
                         self.color[1]/division, self.color[2]/division)
            else:
                color = (0, 0, 0)
            self.texts_surfaces.append(self.font.render(text, True, color))

    def draw_list(self):
        width = 0
        font_width, font_height = self.font.size(" ")
        for surface in self.texts_surfaces:
            width += surface.get_width()
            width += font_width/2
        self.image = pg.Surface((width, font_height), pg.SRCALPHA)
        margin = 0
        for surface in self.texts_surfaces:
            self.image.blit(surface, (margin, 0))
            margin += surface.get_width() + font_width/2
        self.dirty = 1
