import pygame as pg
import os
from rasp_pipboy.utils.config import ConfigSettings
import sys
from rasp_pipboy import Engine


def main():
    """
    Initialize; create an App; and start the main loop.
    """
    mode_flags = pg.DOUBLEBUF | pg.OPENGL
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    framerate = ConfigSettings().framerate
    pg.init()
    pg.display.set_caption(ConfigSettings().caption)
    pg.display.set_mode((ConfigSettings().width, ConfigSettings().height), mode_flags)
    app = Engine(framerate)
    app.main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
