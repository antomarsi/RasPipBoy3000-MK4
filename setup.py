from dotenv import load_dotenv
import os, pygame
from dotenv import load_dotenv
from pathlib import Path

print('CARREGANDO SETTINGS')

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (int(os.getenv('SCREEN_WIDTH', 350)), int(os.getenv('SCREEN_HEIGHT', 428)))
DRAW_COLOR = tuple(int(os.getenv('DRAW_COLOR', 'FFFFFF')[i:i+2], 16) for i in (0, 2 ,4))
MID_COLOR = tuple(int(os.getenv('MID_COLOR', '505050')[i:i+2], 16) for i in (0, 2 ,4))
BACK_COLOR = tuple(int(os.getenv('BACK_COLOR', '000000')[i:i+2], 16) for i in (0, 2 ,4))
TINT_COLOR = tuple(int(os.getenv('TINT_COLOR', '00C800')[i:i+2], 16) for i in (0, 2 ,4))
USE_SOUND = bool(os.getenv('USESOUND', '1'))
MAX_MENUS = int(os.getenv('MAX_MENUS', 5))
SOUND_DIR = os.getenv('SOUND_DIR', 'assets/sounds/new')

pygame.font.init()
fontName = os.getenv('TEXT_FONT')

FONT_SM = pygame.font.Font(fontName, int (SCREEN_HEIGHT * (14.0 / 360)))
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

MINHUMVOL = 0.7
MAXHUMVOL = 1.0
SOUNDS = {}
def loadSound():
    global USE_SOUND, SOUNDS
    if USE_SOUND:
        try:
            print ("Loading sounds...", end='')
            pygame.mixer.init(44100, -16, 2, 2048)
            SOUNDS = {
                "BOOT_SEQUENCE": [
                     pygame.mixer.Sound(SOUND_DIR+'/boot/a.ogg'),
                     pygame.mixer.Sound(SOUND_DIR+'/boot/b.ogg'),
                     pygame.mixer.Sound(SOUND_DIR+'/boot/c.ogg')
                ],
                "UP": [
                     pygame.mixer.Sound(SOUND_DIR+'/UpDown/up_1.ogg'),
                     pygame.mixer.Sound(SOUND_DIR+'/UpDown/up_2.ogg')
                ],
                "LOOP": pygame.mixer.Sound(SOUND_DIR+'/UI_PipBoy_Hum_LP.wav'),
                "ROTARY_VERTICAL": [
                    pygame.mixer.Sound(SOUND_DIR+'/RotaryVertical/rotary_01.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/RotaryVertical/rotary_03.ogg')
                ],
                "ROTARY_HORIZONTAL": [
                    pygame.mixer.Sound(SOUND_DIR+'/RotaryHorizontal/rotary_01.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/RotaryHorizontal/rotary_02.ogg')
                ],
                "LIGHT_ON": [pygame.mixer.Sound(SOUND_DIR+'/UI_PipBoy_LightOn.ogg')],
                "LIGHT_OFF": [pygame.mixer.Sound(SOUND_DIR+'/UI_PipBoy_LightOff.ogg')],
                "BURST_DRIVE_A": [
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_01.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_02.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_03.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_04.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_05.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_06.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_07.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_08.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_09.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_10.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_11.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_12.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_13.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_14.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_15.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_16.ogg'),
                    pygame.mixer.Sound(SOUND_DIR+'/BurstDriveA/bustdrivea_17.ogg'),
                ]
            }
            SOUNDS["LOOP"].set_volume(MINHUMVOL)
            print ("(done)")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            USE_SOUND = False
    print ("SOUND: %s" %(USE_SOUND))
