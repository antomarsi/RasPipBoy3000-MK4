import os
import pygame as pg
from rasp_pipboy.utils.config import ConfigSettings


pg.font.init()
MONOFONTO_12 = pg.font.Font(os.path.join(ConfigSettings().assets_folder, 'fonts', 'monofonto.ttf'), 12)
MONOFONTO_14 = pg.font.Font(os.path.join(ConfigSettings().assets_folder, 'fonts', 'monofonto.ttf'), 14)
MONOFONTO_16 = pg.font.Font(os.path.join(ConfigSettings().assets_folder, 'fonts', 'monofonto.ttf'), 16)
MONOFONTO_18 = pg.font.Font(os.path.join(ConfigSettings().assets_folder, 'fonts', 'monofonto.ttf'), 18)
