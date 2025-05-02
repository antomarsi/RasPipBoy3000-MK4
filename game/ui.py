from core.engine import Entity
from core.resource_loader import ResourceLoader
from typing import Union
from utils.config import config
import pygame as pg

from utils.layout import layout_flex_row, scale_surface_keep_aspect

UI_MARGIN = 14


class Header(Entity):

    def __init__(self, label=None, options=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR):
        super().__init__((config.WIDTH-(UI_MARGIN*2), 75))
        self.rect[0] = UI_MARGIN
        self._label = label
        self.options = [str(x) for x in options]
        self.current_label = None
        self.color = color
        self.bg_color = bg_color
        self.font = ResourceLoader.get_font("MONOFONTO", 41)
        self.update_label(self._label)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if self._label is not value:
            self._label = value
            self.update_label(value)

    def update_label(self, label):
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
            if text == label:
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

    def __init__(self, options=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR, active_index=0):
        super().__init__((config.WIDTH, 43))
        self.color = color
        self.bg_color = bg_color

        self.rect[1] = 70
        self.rect[0] = 80

        self.font = ResourceLoader.get_font("MONOFONTO", 41)
        self._active_index = active_index
        self.options = [str(x) for x in options]
        self.update_label(self._active_index)

    @property
    def active_index(self):
        return self._active_index

    @active_index.setter
    def active_index(self, value):
        if value >= len(self.options):
            raise Exception(f"No SubMenu found for index {value}")
        if value is not self._active_index:
            self._active_index = value
            self.update_label(value)

    def update_label(self, index):
        self.image.fill(self.bg_color)
        margin = 0
        for idx, text in enumerate(self.options):
            division = abs(idx - index) + 1
            if (division > 2):
                division += 2
            if (division <= 5):
                color = (self.color[0] / division,
                         self.color[1]/division, self.color[2]/division)
            else:
                color = self.bg_color
            text_sur = self.font.render(text, True, color).convert_alpha()
            self.image.blit(text_sur, (margin, 0))
            margin += text_sur.get_width() + 18


class Scanlines(Entity):
    _layer = 11

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

    def update(self, deltatime=0, *args, **kwargs):
        self.top += self.speed * deltatime
        if self.top >= self.height + 130:
            self.top = -130
        self.rect[1] = self.top
        super().update(deltatime, *args, **kwargs)


class Overlay(Entity):
    _layer = 10

    def __init__(self):
        super().__init__()
        self.image = ResourceLoader.add_image("overlay", "images/overlay.png")


class Footer(Entity):
    def __init__(self, sections=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR):
        super(Footer, self).__init__((config.WIDTH - UI_MARGIN * 2, 30))
        self.color = color
        self.box_color = color
        self.bg_color = bg_color
        self.rect[0] = UI_MARGIN
        self.rect[1] = config.HEIGHT - 45
        self.sections = sections
        self.font = ResourceLoader.get_font("MONOFONTO", 24)
        self.padding = 4
        self.render()

    def _parse_sections(self):
        sections = []
        for value in self.sections:
                section = value
                size = 1
                if isinstance(value, Union[tuple, list]):
                    section = value[0]
                    indexes = range(len(value))
                    if 1 in indexes:
                        size = value[1]
                sections.append((section, size))
        return sections

    def render(self):
        if self.sections:
            sections = self._parse_sections()


            total_size = sum(x for (_, x) in sections)
            rect_size = (self.rect.width - (self.padding *
                         (total_size-1))) / total_size
            next_pos = 0
            box_color = (self.color[0]/2, self.color[1]/2, self.color[2]/2)

            for (section, size) in sections:

                current_size = (rect_size * size) + (self.padding * (size-1))
                rect = pg.Rect(next_pos, 0, current_size,
                               self.image.get_height())

                pg.draw.rect(self.image, box_color, rect)

                rect.left =- self.padding
                rect.right =- self.padding

                surface = self.get_surface_section(section, rect)

                if isinstance(surface, pg.Surface):
                    self.image.blit(surface, (next_pos + self.padding, 0))

                next_pos += current_size + self.padding

    def get_surface_section(self, value, available_size: pg.Rect):
        if isinstance(value, str):
            return self.font.render(value, True, self.color)
        if isinstance(value, pg.Surface):
            if hasattr(value, "flex"):
                return scale_surface_keep_aspect(value, min(value.get_width(), available_size.width))
            return value
        if isinstance(value, list):
            value = [self.font.render(v, True, self.color) if isinstance(v, str) else v for v in value]
            return layout_flex_row(value, available_size, self.padding)
        raise Exception("Failed to parse surface section")


class ProgressBar(Entity):
    _value = 0

    def __init__(self, dimensions, font=None, color=config.DRAW_COLOR, bg_color=(0, 0, 0, 0), value=0, max_value=1, border_width=1, text_format="{0}"):
        super().__init__(dimensions, flags=pg.SRCALPHA)
        self._value = value
        self.color = color
        self.bg_color = bg_color
        self.border_width = border_width
        self.text_format = text_format
        self.font = font
        self._max_value = max_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value > self._max_value:
            raise ValueError("Value cannot be bigger than max value")
        self._value = value
        self.update_draw()

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        self._max_value = value
        self.update_draw()

    def update_draw(self):
        self.image.fill(self.bg_color)

        if self.font:
            pass

        fill_value = self._value / self._max_value

        pg.draw.rect(self.image, self.color, pg.Rect(
            0, 0, self.rect.width*fill_value, self.rect.height))

        pg.draw.rect(self.image, self.color, self.rect, self.border_width)
