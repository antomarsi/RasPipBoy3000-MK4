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

        self.options = [str(x) for x in options]

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
            next_position += text_sur.get_width() + 40

    def set_active(self, index: int):
        if len(self.options) - 1 > index:
            raise Exception(f"No header found for index {index}")
        if self.selected_index != index:
            self.selected_index = index
            self.dirty = 1

    def render(self, *args, **kwargs):
        if self._active_index == self.selected_index:
            return
        self._active_index = self.selected_index
        self.image.fill(self.bg_color)
        LINE_WIDTH = 2
        margin = 14
        short_line_margin = 10
        lines_selection = []

        lines_selection.append((margin, self.rect.height))
        lines_selection.append((margin, self.rect.height-short_line_margin))
        next_position = 100
        selected_position = 0
        selected_text = None
        for index, text in enumerate(self.options):
            next_position += 14
            text_surface = self.font.render(f"{text}", True, self.color)
            if index == self.selected_index:
                selected_position = next_position
                selected_text = text_surface
                continue
            next_position += text_surface.get_width() + 40
            self.image.blit(text_surface, (next_position, 22))

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
            (self.rect.width-margin, self.rect.height-short_line_margin))
        lines_selection.append((self.rect.width-margin, self.rect.height))

        pg.draw.lines(self.image, self.color, False,
                      lines_selection, LINE_WIDTH)

        pg.draw.rect(self.image, self.bg_color, (selected_position -
                     6, 32, selected_text.get_width() + 12, 12))
        self.image.blit(selected_text, (selected_position, 22))
        self.dirty = 0


class SubMenu(Entity):
    options = []
    def __init__(self, options=[], color=config.DRAW_COLOR, bg_color=config.BG_COLOR, selected_index=0, visible=True):
        super().__init__((config.WIDTH, 50))
        self.color = color
        self.bg_color = bg_color

        self.rect[1] = 78
        self.rect[0] = 93

        self.font = ResourceLoader.getInstance().get_font("ROBOTO_B", 41)
        self.visible = visible
        self.selected_index = selected_index
        self._active_index = -1
        self.set_options(options)
        self.dirty = 1

    def set_options(self, options):
        self.options = [str(x) for x in options]
        self.dirty = 1

    def set_active_index(self, index: int):
        if index >= len(self.options):
            raise Exception(f"No SubMenu found for index {index}")
        if self.selected_index != index:
            self.selected_index = index
            self.dirty = 1


    def render(self, interval=0, *args, **kwargs):
        if self._active_index == self.selected_index:
            return
        self.image.fill(self.bg_color)
        self._active_index = self.selected_index
        margin = 0
        for idx, text in enumerate(self.options):
            division = abs(idx - self.selected_index) + 1
            if (division > 2):
                division += 2
            if (division <= 5):
                color = (self.color[0] / division,
                            self.color[1]/division, self.color[2]/division)
            else:
                color = self.bg_color
            print(text, color)
            text_sur = self.font.render(text, True, color).convert_alpha()
            self.image.blit(text_sur, (margin, 0))
            margin += text_sur.get_width() + 13


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

    def update(self, deltatime=0, *args, **kwargs):
        if deltatime >= self.animation_time:
            self.top = self.top + self.speed
            if self.top >= self.height + 130:
                self.top = -130
            self.rect[1] = self.top
        super().update(deltatime, *args, **kwargs)


class Overlay(Entity):
    def __init__(self):
        super().__init__()
        self.image = ResourceLoader.getInstance().get_image("overlay")
