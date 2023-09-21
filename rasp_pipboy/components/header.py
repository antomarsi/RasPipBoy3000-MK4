import pygame as pg
import rasp_pipboy.graphics.fonts as fonts


class Header(pg.sprite.DirtySprite):
    def __init__(self, rect, color=(255, 255, 255), selected_index=0):
        pg.sprite.DirtySprite.__init__(self)
        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.rect = rect
        self.texts = [
            {"title": "STAT", "pos": 51},
            {"title": "INV", "pos": 107},
            {"title": "DATA", "pos": 156},
            {"title": "MAP", "pos": 217},
            {"title": "RADIO", "pos": 267}
        ]
        self.color = color
        self.selected_index = selected_index
        self.draw_header()

    def get_selected_index_position(self):
        return self.texts[self.selected_index]["pos"] + self.rect.x - 9

    def get_start_line_x(self):
        return self.rect.width

    def draw_header(self):
        margin = 0

        lines_selection = []
        lines_selection.append((margin, self.rect.height))
        lines_selection.append((margin, self.rect.height-8))

        selected_item = self.texts[self.selected_index]["title"]
        font = fonts.MONOFONTO_16
        font.set_bold(True)
        for text in self.texts:
            name = text['title']
            position = text['pos']
            text_sur = font.render(name, True, self.color)
            self.image.blit(text_sur, (position, 7))
            if selected_item == name:
                lines_selection.append((position - 4, self.rect.height-8))
                lines_selection.append((position - 4, self.rect.height-22))
                lines_selection.append((position - 2, self.rect.height-22))
                pg.draw.lines(self.image, self.color,
                              False, lines_selection, 2)
                lines_selection.clear()
                lines_selection.append(
                    (position + text_sur.get_width() + 2, self.rect.height-22))
                lines_selection.append(
                    (position + text_sur.get_width() + 4, self.rect.height-22))
                lines_selection.append(
                    (position + text_sur.get_width() + 4, self.rect.height-8))
        lines_selection.append((self.rect.width-2, self.rect.height-8))
        lines_selection.append((self.rect.width-2, self.rect.height))
        pg.draw.lines(self.image, self.color, False, lines_selection, 2)
        self.dirty = 1
