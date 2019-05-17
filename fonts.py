import os
import pygame as pg

pg.font.init()
MONOFONTO_12 = pg.font.Font(os.path.join(os.path.dirname(
    __file__), 'assets', 'fonts', 'monofonto.ttf'), 12)
MONOFONTO_14 = pg.font.Font(os.path.join(os.path.dirname(
    __file__), 'assets', 'fonts', 'monofonto.ttf'), 14)
MONOFONTO_16 = pg.font.Font(os.path.join(os.path.dirname(
    __file__), 'assets', 'fonts', 'monofonto.ttf'), 16)
MONOFONTO_18 = pg.font.Font(os.path.join(os.path.dirname(
    __file__), 'assets', 'fonts', 'monofonto.ttf'), 18)
