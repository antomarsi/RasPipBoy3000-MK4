from core.engine import Entity
from core.resource_loader import ResourceLoader
from utils.config import config
import pygame as pg


class Header(Entity):

    def __init__(self, options, color=config.DRAW_COLOR, bg_color=config.BG_COLOR, selected_index=0):
        super().__init__((config.WIDTH, 75))
        self.color = color
        self.bg_color = bg_color
        self.selected_index = selected_index
        self._active_index = -1
        self.font = ResourceLoader.getInstance().get_font("ROBOTO_B", 41)
        self.dirty = 1
        self.center_option = 0

        self.set_options(options)

    def set_options(self, options):
        if not options:
            raise Exception("Header Options cannot be empty")
        self.options = []
        next_position = 100

        for index, option in enumerate(options):
            next_position += 14
            text_sur = self.font.render(
                f"{option}", True, self.color)
            self.options.append({"surf": text_sur, "position": next_position})
            if self.selected_index == index:
                self.center_option = next_position + (text_sur.get_width() / 2)
            next_position += text_sur.get_width() + 40



    def set_active(self, index: int):
        if len(self.options) - 1 > index:
            raise Exception(f"No header found for index {index}")
        self.selected_index = index
        self.dirty = 1

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

    def render(self, *args, **kwargs):
        if self._active_index == self.selected_index:
            return
        self._active_index = self.selected_index

        LINE_WIDTH = 2
        margin = 14
        short_line_margin = 10
        lines_selection = []

        lines_selection.append((margin, self.rect.height))
        lines_selection.append((margin, self.rect.height-short_line_margin))
        for index, text_surface in enumerate(self.options):
            if index == self.selected_index:
                continue
            position = text_surface.get("position")
            self.image.blit(
                text_surface.get("surf"), (position, 22))

        selected_position = self.options[self.selected_index].get("position")
        selected_text = self.options[self.selected_index].get("surf")

        if self.selected_index == index:
                self.center_option = selected_position + (selected_text.get_width() / 2)

        selected_margin = 38
        selected_line_margin = 14
        lines_selection.append(
            (selected_position-selected_line_margin-1, self.rect.height-short_line_margin))
        lines_selection.append((selected_position-selected_line_margin-1, selected_margin))
        lines_selection.append(
            (selected_position+selected_line_margin-1+selected_text.get_width(), selected_margin))
        lines_selection.append(
            (selected_position+selected_line_margin-1+selected_text.get_width(), self.rect.height-short_line_margin))

        lines_selection.append(
            (self.rect.width-margin, self.rect.height-short_line_margin))
        lines_selection.append((self.rect.width-margin, self.rect.height))

        pg.draw.lines(self.image, self.color, False,
                      lines_selection, LINE_WIDTH)

        pg.draw.rect(self.image, self.bg_color, (selected_position-6, 32, selected_text.get_width() + 12, 12))
        self.image.blit(selected_text, (selected_position, 22))

        super().update(*args, **kwargs)
        self.dirty = 0


class SubMenu(Entity):
    options = []
    active = False
    def __init__(self, options=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR, selected_index=0):
        super().__init__((config.WIDTH, 36))
        self.color = color
        self.bg_color = bg_color

        self.rect[0] = 73
        self.rect[1] = 93

        self.font = ResourceLoader.getInstance().get_font("ROBOTO_B", 33)

        self.selected_index = selected_index
        self._active_index = -1
        if options:
            self.set_options(options)

    def set_options(self, options):
        prev_text_width = None
        spacing = 40
        text_pos = 0
        for option in options:
            text_sur = self.font.render(
                f"{option}", True, self.color, self.bg_color)
            if not prev_text_width:
                prev_text_width = text_sur.get_width()
                text_pos = 104 - spacing - prev_text_width
            text_pos = text_pos + prev_text_width + spacing
            self.options.append({"surf": text_sur, "position": text_pos})
            prev_text_width = text_sur.get_width()

    def set_active(self, index: int):
        if len(self.options) - 1 > index:
            raise Exception(f"No SubMenu found for index {index}")
        self.selected_index = index
        self.dirty = 1

    def render(self, interval=0, *args, **kwargs):
        if self.active:
            self.image.fill((255, 0, 0))

        return super().render(interval, *args, **kwargs)

class Footer(Entity):

    def __init__(self, color=config.DRAW_COLOR, dimensions=config.SIZE, *args, **kwargs):
        self.menu = []
        self.color = color
        super().__init__(dimensions, *args, **kwargs)
        self.rect[0] = 14
        self.rect[1] = dimensions[1] - 40

    def render(self, interval=0, *args, **kwargs):
        self.image.fill(self.color)
        return super().render(interval, *args, **kwargs)

class Scanlines(Entity):

    def __init__(self, size=(config.WIDTH, 129), height=config.HEIGHT):
        super().__init__(size)
        self.height = height
        self.image = ResourceLoader.getInstance().get_image("scanline")
        self.rectimage = self.image.get_rect()
        self.rect[1] = 0
        self.top = -130
        self.speed = 10
        self.clock = pg.time.Clock()
        self.animation_time = 0.05
        self.prev_time = 0
        self.dirty = 2

    def render(self, deltatime, *args, **kwargs):
        if deltatime >= self.animation_time:
            self.top = self.top + self.speed
            if self.top >= self.height + 130:
                self.top = -130
            self.rect[1] = self.top
        super().render(self, *args, **kwargs)

class Overlay(Entity):
    def __init__(self):
        super(Overlay, self).__init__()
        self.image = ResourceLoader.getInstance().get_image("overlay")
