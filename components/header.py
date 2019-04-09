import pygame as pg
import fonts

class Header(pg.sprite.DirtySprite):
    def __init__(self, rect, color=(255,255,255), selected_index=0):
        pg.sprite.DirtySprite.__init__(self)
        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.rect = rect
        self.texts = { "STAT": 110, "INV":168, "DATA":215, "MAP":276, "RADIO":325 }
        self.color = color
        self.selected_index = selected_index
        self.draw_header()

    def draw_header(self):
        margin = 56

        lines_selection = []
        lines_selection.append((margin, self.rect.height))
        lines_selection.append((margin, self.rect.height-8))

        selected_item = list(self.texts)[self.selected_index]
        font = fonts.MONOFONTO_16
        font.set_bold(True)
        for name, position in self.texts.items():
            text_sur = font.render(name, True, self.color)
            self.image.blit(text_sur, (position, 7))
            if selected_item == name:
                lines_selection.append((position - 4, self.rect.height-8))
                lines_selection.append((position - 4, self.rect.height-22))
                lines_selection.append((position - 2, self.rect.height-22))
                pg.draw.lines(self.image, self.color, False, lines_selection, 2)
                lines_selection.clear()
                lines_selection.append((position + text_sur.get_width() + 2, self.rect.height-22))
                lines_selection.append((position + text_sur.get_width() + 4, self.rect.height-22))
                lines_selection.append((position + text_sur.get_width() + 4, self.rect.height-8))
        lines_selection.append((self.rect.width - margin, self.rect.height-8))
        lines_selection.append((self.rect.width - margin, self.rect.height))
        pg.draw.lines(self.image, self.color, False, lines_selection, 2)
        self.dirty = 1

    def update(self, dt):
        self.dirty = 1
