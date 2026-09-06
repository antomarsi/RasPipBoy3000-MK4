from core.engine import Entity
from core.resource_loader import ResourceLoader
from typing import Union
from utils.settings import config
from game.data.store import theme
import pygame as pg
from os.path import join

from utils.layout import layout_flex_row, load_svg, scale_surface_keep_aspect

UI_MARGIN = 14


class Header(Entity):

    def __init__(self, label=None, options=[], color=theme.draw_color, bg_color=theme.bg_color):
        super().__init__((config.WIDTH-(UI_MARGIN*2), 60))
        self.rect[0] = UI_MARGIN
        self._label = label
        self.options = [str(x) for x in options]
        self.current_label = None
        self.color = color
        self.bg_color = bg_color
        self.font = ResourceLoader.get_font("MONOFONTO", 30)
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
            self.image.blit(text_surface, (next_position, 14))
            next_position += tab_spacing + text_surface.get_width()

        selected_margin = 28
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
                     6, 26, selected_text.get_width() + 12, 12))
        self.image.blit(selected_text, (selected_position, 14))


class SubMenu(Entity):
    options = []

    def __init__(self, options=[], color=theme.draw_color, bg_color=theme.bg_color, active_index=0):
        super().__init__((config.WIDTH - 80, 32))
        self.color = color
        self.bg_color = bg_color

        self.rect[1] = 54
        self.rect[0] = 80

        self.font = ResourceLoader.get_font("MONOFONTO", 30)
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


class Footer(Entity):
    def __init__(self, sections=[], color=theme.draw_color, bg_color=theme.bg_color):
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

    def update_section(self, index, value):
        if index >= len(self.sections):
            raise Exception("Index not found")
        if self.sections[index] != value:
            self.sections[index] = value
            return True
        return False

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

    def render(self, render_only_indexes=None):
        if self.sections:
            sections = self._parse_sections()

            total_size = sum(x for (_, x) in sections)
            rect_size = (self.rect.width - (self.padding *
                         (total_size-1))) / total_size
            next_pos = 0
            box_color = (self.color[0]/2, self.color[1]/2, self.color[2]/2)

            for idx, (section, size) in enumerate(sections):
                not_skip = not render_only_indexes or idx in render_only_indexes
                current_size = (rect_size * size) + (self.padding * (size-1))
                rect = pg.Rect(next_pos, 0, current_size,
                               self.image.get_height())
                if not_skip:
                    pg.draw.rect(self.image, box_color, rect)

                rect.left = - self.padding
                rect.right = - self.padding

                surface = self.get_surface_section(section, rect)

                if isinstance(surface, pg.Surface) and not_skip:
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
            value = [self.font.render(v, True, self.color) if isinstance(
                v, str) else v.image for v in value]
            return layout_flex_row(value, available_size, self.padding*2)
        raise Exception("Failed to parse surface section")


class ProgressBar(Entity):
    _value = 0

    def __init__(self, dimensions, font=None, color=theme.draw_color, bg_color=(0, 0, 0, 0), value=0, max_value=1, border_width=1, text_format="{0}", margin=(0, 0, 0, 0)):
        super().__init__(dimensions)
        self.image = self.image.convert_alpha()
        self._value = value
        self.color = color
        self.bg_color = bg_color
        self.border_width = border_width
        self.text_format = text_format
        self.font = font
        self._max_value = max_value
        self.margin = margin
        self.update_draw()

    def set_rect(self, size):
        self.image = pg.Surface(size, flags=pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update_draw()

    def on_flex(self, new_size):
        self.set_rect(new_size)

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

        fill_value = self._value / self._max_value
        draw_rect = self.rect.copy()
        draw_rect.top += self.margin[1]
        draw_rect.left += self.margin[0]
        draw_rect.width -= self.margin[2] + self.margin[0]
        draw_rect.height -= self.margin[3] + self.margin[1]

        if self.font:
            # TODO implement text to progress bar
            pass

        pg.draw.rect(self.image, self.color, pg.Rect(
            draw_rect.left, draw_rect.top, (draw_rect.width)*fill_value, draw_rect.height))
        pg.draw.rect(self.image, self.color, draw_rect, self.border_width)


class Menu(Entity):
    def __init__(self, items=[], callback=[], selected=0, color=theme.draw_color, bg_color=theme.bg_color, max_items = 7):
        super().__init__((config.WIDTH - UI_MARGIN*2, config.HEIGHT - 172))
        self.items = items
        self.color = color
        self.soft_color = (color[0]*0.65, color[1]*0.65, color[2]*0.65)
        self.bg_color = bg_color
        self.rect.top = 92
        self.rect.left = UI_MARGIN

        self.callback = callback

        self.index = 0
        self.font = ResourceLoader.get_font("MONOFONTO", 24)

        self.menu_item_size = 38
        self.max_items = max_items
        self.selected = selected

        # Create arrow surfaces
        self.arrow_up = load_svg(join(ResourceLoader._asset_folder, "images/arrow.svg"), 13, 13, self.soft_color)
        self.arrow_down = pg.transform.flip(self.arrow_up, False, True)

        self.render()

    def select(self, value):
        value = min(max(value, 0), len(self.items)-1)
        if self.selected != value:
            if value > self.index + self.max_items - 1:
                self.index = value - self.max_items + 1
            if self.index > value:
                self.index = value
            self.selected = value
            self.render()

    def render(self):
        pg.draw.rect(self.image, self.color,
                     (0, 0, self.rect.width*0.45, self.menu_item_size))
        item_count = 0

        for idx, item in enumerate(self.items):
            if idx < self.index or item_count >= self.max_items:
                continue
            item_count += 1
            position_y = (idx - self.index) * self.menu_item_size
            surf = self.generate_item(item, idx == self.selected)
            self.image.blit(surf, (0, position_y))
        # TODO implement arrows
        # if True:
        #     self.image.blit(self.arrow_up, (10, 0))
        #     self.image.blit(self.arrow_down, (10, self.menu_item_size * self.max_items - 20))

    def generate_item(self, text, selected=False):
        surface = pg.Surface((self.rect.width*0.55, self.menu_item_size))
        text_color = self.soft_color
        if selected:
            text_color = self.bg_color
            surface.fill(self.soft_color)
        font_surf = self.font.render(text, True, text_color)
        surface.blit(
            font_surf, (20, surface.get_rect().centery - font_surf.get_height()/2))
        return surface
