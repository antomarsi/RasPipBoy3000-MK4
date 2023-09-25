import pygame as pg
import os
from rasp_pipboy.utils.config import ConfigSettings
import sys
from rasp_pipboy import Engine


def main():
    """
    Initialize; create an App; and start the main loop.
    """
    print("initializing app")
    mode_flags = pg.DOUBLEBUF | pg.OPENGL | pg.SCALED
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    framerate = ConfigSettings().framerate
    print("Pygame Display init")
    pg.display.init()
    print("Pygame Mixer pre init")
    pg.mixer.pre_init(44100, 16, 2, 4096)
    print("Pygame Mixer init")
    pg.mixer.init()
    print("Pygame font init")
    pg.font.init()
    print("Finished Pygame init")
    pg.display.set_caption(ConfigSettings().caption)
    pg.display.set_mode((ConfigSettings().width, ConfigSettings().height), mode_flags)
    app = Engine(framerate)
    app.main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
