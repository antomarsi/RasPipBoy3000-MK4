
from game.modules import BaseModule, SubModule
from game.ui import Footer, Header, Menu
from utils.settings import config
import pygame as pg


class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
            RadioSubModule(self)
        ]
        super().__init__(pipboy, *sprites, **kwargs)
        self.header = Header(label=str(self), options=config.MODULE_TEXTS)
        self.footer = Footer([""])
        self.add(self.footer)
        self.add(self.header)

    def handle_resume(self):
        self.switch_submodule(0)
        return super().handle_resume()



    def __str__(self):
        return "RADIO"


class RadioSubModule(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)
        radios = [
            "1 Classical Radio",
            "2 Diamond City Radio",
            "3 Diamond City Radio",
            "4 Diamond City Radio",
            "5 Diamond City Radio",
            "6 Diamond City Radio",
            "7 Diamond City Radio",
            "8 Diamond City Radio",
            "9 Diamond City Radio",
            "10 Diamond City Radio",
            "11 Diamond City Radio",
        ]
        self.radio_menu = RadioMenu(radios, max_items=9)
        self.add(self.radio_menu)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.radio_menu.select(self.radio_menu.selected - 1)
            elif event.key == pg.K_DOWN:
                self.radio_menu.select(self.radio_menu.selected + 1)
        return super().handle_event(event)

    def __str__(self):
        return ""


class RadioMenu(Menu):
    radio_grid = None

    def __init__(self, items=..., callback=..., selected=0, color=config.DRAW_COLOR, bg_color=config.BG_COLOR, max_items=7):
        super().__init__(items, callback, selected, color, bg_color, max_items)
        self.generate_radio_grid()
        self.render()

    def generate_radio_grid(self):
        self.radio_grid = pg.Surface(
            (self.rect.width*0.3, self.rect.width*0.3))
        radio_grid_rect = self.radio_grid.get_rect()
        bottom = radio_grid_rect.height
        right = radio_grid_rect.width

        pg.draw.lines(self.radio_grid, self.soft_color,
                      False, [(0, bottom - 2), (right-2, bottom - 2), (right - 2, 0)], 2)
        long_line = 8
        long_lines = 9
        short_line = 6
        short_lines = long_lines * 4
        line_start = 0

        line_x = int(bottom / long_lines)
        short_line_x = line_x / 3

        short_line_start = 0
        for i in range(3):
            pg.draw.line(self.radio_grid, self.soft_color, (short_line_start,
                         bottom), (short_line_start, bottom - short_line), 1)
            pg.draw.line(self.radio_grid, self.soft_color, (right,
                         short_line_start), (right - short_line, short_line_start), 1)
            short_line_start += short_line_x

        for _ in range(long_lines):
            line_start += line_x
            short_line_start = line_start
            for i in range(3):
                pg.draw.line(self.radio_grid, self.soft_color, (short_line_start,
                             bottom), (short_line_start, bottom - short_line), 1)
                pg.draw.line(self.radio_grid, self.soft_color, (right,
                             short_line_start), (right - short_line, short_line_start), 1)
                short_line_start += short_line_x
            pg.draw.line(self.radio_grid, self.soft_color, (line_start,
                         bottom), (line_start, bottom - long_line), 1)
            pg.draw.line(self.radio_grid, self.soft_color, (right,
                         line_start), (right - long_line, line_start), 1)

    def render(self):
        super().render()
        if self.radio_grid:
            self.image.blit(self.radio_grid, (self.rect.width*0.65, 0))
