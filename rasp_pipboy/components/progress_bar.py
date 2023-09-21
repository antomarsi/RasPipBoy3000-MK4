import pygame as pg
import rasp_pipboy.graphics.fonts as fonts


class ProgressBar(pg.sprite.DirtySprite):
    def __init__(self, rect, color=(255, 255, 255), background_color=(0, 0, 0), value=0, max_value=1, border_width=2, text_format="{0}"):
        pg.sprite.DirtySprite.__init__(self)
        self.image = pg.Surface(rect.size)
        self.rect = rect
        self.__value = value
        self.__max_value = max_value
        self.border_width = border_width
        self.color = color
        self.background_color = background_color
        self.font = fonts.MONOFONTO_12
        self.text_format = text_format

        self.redraw()

    def set_max_value(self, value):
        self.__max_value = value
        self.redraw()

    def set_value(self, value):
        self.__value = value
        self.redraw()

    def redraw(self):
        self.image.fill(self.color)
        self.unfill_rect = self.rect.copy()
        self.unfill_rect.top = self.border_width
        self.unfill_rect.left = self.border_width
        self.unfill_rect.width -= self.border_width*2
        self.unfill_rect.height -= self.border_width*2
        perc = (self.__value / self.__max_value)

        self.unfill_rect.width -= (1-(self.__value /
                                      self.__max_value)) * self.unfill_rect.width

        pg.draw.rect(self.image, self.background_color, self.unfill_rect)

        text_s = self.font.render(self.text_format.replace('{0}', str(
            int((self.__value / self.__max_value)*100))+'%'), True, (0, 0, 0))

        self.image.blit(text_s, (self.image.get_width(
        )/2 - text_s.get_width()/2, (self.image.get_height()/2 - text_s.get_height()/2)))

        text_s = self.font.render(self.text_format.replace('{0}', str(
            int((self.__value / self.__max_value)*100))+'%'), True, (255, 255, 255))
        text_sur = pg.Surface(self.image.get_size(), pg.SRCALPHA)

        text_sur.blit(text_s, (self.image.get_width()/2 - text_s.get_width()/2,
                               (self.image.get_height()/2 - text_s.get_height()/2) + self.border_width))
        self.image.blit(text_sur.subsurface(self.unfill_rect), (0, 0))

        text_sur = pg.Surface(self.image.get_size(), pg.SRCALPHA)

        text_sur = pg.Surface(self.image.get_size(), pg.SRCALPHA)
        text_s = self.font.render(self.text_format.replace('{0}', str(
            int((self.__value / self.__max_value)*100))+'%'), True, (0, 0, 0))
        text_sur.blit(text_s, (self.image.get_width()/2 - text_s.get_width()/2,
                               (self.image.get_height()/2 - text_s.get_height()/2) + self.border_width))

        self.dirty = 1
