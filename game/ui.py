from core.engine import Entity
from typing import Union
from core.resource_loader import ResourceLoader
from utils.config import config
import pygame as pg

UI_MARGIN = 14


class Header(Entity):

    def __init__(self, label=None, options=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR):
        super().__init__((config.WIDTH-(UI_MARGIN*2), 75))
        self.rect[0] = UI_MARGIN
        self.label = label
        self.options = [str(x) for x in options]
        self.current_label = None
        self.color = color
        self.bg_color = bg_color
        self.font = ResourceLoader.get_font("MONOFONTO", 41)

    def render(self, *args, **kwargs):
        if self.current_label == self.label:
            return
        self.current_label = self.label
        self.image.fill(self.bg_color)
        LINE_WIDTH = 3
        short_line_margin = 10
        lines_selection = []

        lines_selection.append((2, self.rect.height))
        lines_selection.append((2, self.rect.height-short_line_margin))
        next_position = 80
        selected_position = 0
        selected_text = None

        tab_area_width = config.WIDTH * 0.8
        tab_spacing = tab_area_width / (len(self.options) - 1)

        text_surfaces = []
        current_index = None
        for idx, text in enumerate(self.options):
            if text == self.current_label:
                current_index = idx
            text_surf = self.font.render(f"{text}", True, self.color)
            tab_area_width -= text_surf.get_width()
            text_surfaces.append(text_surf)
        tab_spacing = tab_spacing / (len(self.options) - 1)

        for index, text_surface in enumerate(text_surfaces):
            if index == current_index:
                selected_position = next_position
                selected_text = text_surface
                next_position += tab_spacing + text_surface.get_width()
                continue
            self.image.blit(text_surface, (next_position, 22))
            next_position += tab_spacing + text_surface.get_width()

        selected_margin = 38
        selected_line_margin = 14
        lines_selection.append(
            (selected_position-selected_line_margin-1, self.rect.height-short_line_margin))
        lines_selection.append(
            (selected_position-selected_line_margin-1, selected_margin))
        lines_selection.append(
            (selected_position+selected_line_margin-1+selected_text.get_width(), selected_margin))
        lines_selection.append(
            (selected_position+selected_line_margin-1+selected_text.get_width(), self.rect.height-short_line_margin))

        lines_selection.append(
            (self.rect.width - 2, self.rect.height-short_line_margin))
        lines_selection.append((self.rect.width-2, self.rect.height))

        pg.draw.lines(self.image, self.color, False,
                      lines_selection, LINE_WIDTH)

        pg.draw.rect(self.image, self.bg_color, (selected_position -
                     6, 32, selected_text.get_width() + 12, 12))
        self.image.blit(selected_text, (selected_position, 22))


class SubMenu(Entity):
    options = []

    def __init__(self, options=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR, selected_index=0):
        super().__init__((config.WIDTH, 50))
        self.color = color
        self.bg_color = bg_color

        self.rect[1] = 70
        self.rect[0] = 80

        self.font = ResourceLoader.get_font("MONOFONTO", 41)
        self.selected_index = selected_index
        self._active_index = None
        self.options = [str(x) for x in options]

    def set_active_index(self, index: int):
        if index >= len(self.options):
            raise Exception(f"No SubMenu found for index {index}")
        if self.selected_index != index:
            self.selected_index = index

    def render(self, *args, **kwargs):
        if self._active_index == self.selected_index:
            return
        self.image.fill(self.bg_color)
        self._active_index = self.selected_index
        margin = 0
        for idx, text in enumerate(self.options):
            division = abs(idx - self._active_index) + 1
            if (division > 2):
                division += 2
            if (division <= 5):
                color = (self.color[0] / division,
                         self.color[1]/division, self.color[2]/division)
            else:
                color = self.bg_color
            text_sur = self.font.render(text, True, color, self.bg_color)
            self.image.blit(text_sur, (margin, 0))
            margin += text_sur.get_width() + 18


class Scanlines(Entity):

    def __init__(self, size=(config.WIDTH, 129), height=config.HEIGHT):
        super().__init__(size)
        self.height = height
        self.image = ResourceLoader.add_image(
            "scanline", "images/scanline.png")
        self.rectimage = self.image.get_rect()
        self.rect[1] = 0
        self.top = -130
        self.speed = 100
        self.prev_time = 0
        self.dirty = 2

    def update(self, deltatime=0, *args, **kwargs):
        self.top += self.speed * deltatime
        if self.top >= self.height + 130:
            self.top = -130
        self.rect[1] = self.top
        super().update(deltatime, *args, **kwargs)


class Overlay(Entity):
    def __init__(self):
        super().__init__()
        self.image = ResourceLoader.add_image("overlay", "images/overlay.png")


class Footer(Entity):
    def __init__(self, sections=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR):
        super(Footer, self).__init__((config.WIDTH - UI_MARGIN * 2, 30))
        self.color = color
        self.box_color = color
        self.rect[0] = UI_MARGIN
        self.rect[1] = config.HEIGHT - 45
        self.sections = [[x, 1] if isinstance(x, str) else x for x in sections]
        self.font = ResourceLoader.get_font("MONOFONTO", 24)
        self.padding = 4

    def render(self):
        if self.sections:
            total_size = sum(x for (_, x) in self.sections)
            rect_size = (self.rect.width - (self.padding *
                         (total_size-1))) / total_size
            next_pos = 0
            box_color = (self.color[0]/2, self.color[1]/2, self.color[2]/2)
            for (text, size) in self.sections:
                current_size = (rect_size * size) + (self.padding * (size-1))
                rect = pg.Rect(next_pos, 0, current_size,
                               self.image.get_height())

                pg.draw.rect(self.image, box_color, rect)

                surface = None
                if str(text):
                    surface = self.font.render(text, True, (255, 255, 255))

                if isinstance(surface, pg.Surface):
                    self.image.blit(surface, (next_pos + self.padding, 0))

                next_pos += current_size + self.padding
