import pygame as pg
import os
from utils.settings import config
from game.pipboy import PipBoy
from utils.logger import logger


def main():
    if config.GPIO_AVALIABLE:
        import RPi.GPIO as GPIO  # type: ignore
        GPIO.setmode(GPIO.BCM)

        os.environ('SDL_VIDEODRIVER', 'fbcon')
        os.environ('SDL_FBDEV', '/dev/fb1')
        os.environ('SDL_MOUSEDRV', 'TSLIB')
        os.environ('SDL_MOUSEDEV', '/dev/input/touchscreen')
    """
    Initialize; create an App; and start the main loop.
    """
    logger.debug("Initializing app..")

    # os.environ['SDL_VIDEO_CENTERED'] = '1'
    try:
        pg.mixer.init(44100, -16, 2, 2048)
        config.SOUND_ENABLED = True
    except:
        pass
    logger.info("Running...")
    pipboy = PipBoy(title="RasPipBoy-3000 Mk IV",
                    size=config.SIZE, output_size=config.OUTPUT_SIZE)
    pipboy.run()


if __name__ == "__main__":
    main()
