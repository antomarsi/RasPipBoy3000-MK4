import os, pygame
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (int(os.getenv('SCREEN_WIDTH')), int(os.getenv('SCREEN_HEIGHT')))
DRAW_COLOR = tuple(int(os.getenv('DRAW_COLOR', '#FFFFFF')[i:i+2], 16) for i in (0, 2 ,4))
BACK_COLOR = tuple(int(os.getenv('BACK_COLOR', '#000000')[i:i+2], 16) for i in (0, 2 ,4))
TINT_COLOR = tuple(int(os.getenv('TINT_COLOR', '#00C800')[i:i+2], 16) for i in (0, 2 ,4))
MAX_MENUS = int(os.getenv('MAX_MENUS', 5))

pygame.font.init()
fontName = os.getenv('TEXT_FONT')

FONT_SM = pygame.font.Font(fontName, int (SCREEN_HEIGHT * (12.0 / 360)))
FONT_MD = pygame.font.Font(fontName, int (SCREEN_HEIGHT * (16.0 / 360.0)))
FONT_LG = pygame.font.Font(fontName, int (SCREEN_HEIGHT * (24.0 / 360.0)))

tempImg = FONT_SM.render("X", True, DRAW_COLOR, (0, 0, 0))
SM_SIZE = SM_WIDTH, SM_HEIGHT = (tempImg.get_width(), tempImg.get_height())
del tempImg

tempImg = FONT_MD.render("X", True, DRAW_COLOR, (0, 0, 0))
MD_SIZE = MD_WIDTH, MD_HEIGHT = (tempImg.get_width(), tempImg.get_height())
del tempImg

tempImg = FONT_LG.render("X", True, DRAW_COLOR, (0, 0, 0))
LG_SIZE = LG_WIDTH, LG_HEIGHT = (tempImg.get_width(), tempImg.get_height())
del tempImg
