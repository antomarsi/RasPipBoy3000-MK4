import os
import sys
import struct
import moderngl
import pygame as pg
from pygame.locals import *
from rasp_pipboy.utils.config import ConfigSettings
from rasp_pipboy.utils.shaders import Shader
from rasp_pipboy.scenes.intro import IntroScene
from scanline_gradient import ScanLineGradient

class App(object):
    """
    Class responsible for program control flow.
    """

    def __init__(self, fps):
        self.screen = pg.Surface(pg.display.get_surface().get_size()).convert(
            (16711680, 65280, 255, 0), 0)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = fps
        self.done = False
        self.keys = pg.key.get_pressed()


        self.active_scene = IntroScene(skip_intro=ConfigSettings().skip_intro)

        self.shader = Shader(self.screen)

        self.font = pg.font.Font(None, 30)
        self.show_fps = False
        self.sprite_list = pg.sprite.LayeredDirty((ScanLineGradient()))

    def event_loop(self):
        pressed_keys = pg.key.get_pressed()
        filtered_events = []
        for event in pg.event.get():
            if event.type == QUIT:
                self.done = True
            elif event.type == KEYDOWN:
                if event.key == K_F3:
                    self.show_fps = not self.show_fps
                elif event.key == K_ESCAPE:
                    self.done = True
            if self.done == True and self.active_scene != None:
                self.active_scene.terminate()
            else:
                filtered_events.append(event)

        if self.active_scene != None:
            self.active_scene.process_input(filtered_events, pressed_keys)

    def update(self, dt):
        """
        Update must acccept and pass dt to all elements that need to update.
        """
        if self.active_scene != None:
            self.active_scene.update(dt)
        self.sprite_list.update(dt)

    def render(self):
        """
        Render all needed elements and update the display.
        """
        self.screen.fill(cfg.background_color)

        if self.active_scene != None:
            self.active_scene.render(self.screen)
        self.sprite_list.draw(self.screen)

        if self.show_fps:
            self.screen.blit(self.font.render(
                str(int(self.clock.get_fps())), True, pg.Color('white')), (10, 10))

        self.shader.render(self.screen)
        pg.display.flip()

    def main_loop(self):
        """
        We now use the return value of the call to self.clock.tick to
        get the time delta between frames.
        """
        dt = 0
        self.clock.tick(self.fps)
        while not self.done:
            self.event_loop()
            self.update(dt)
            self.render()
            if self.active_scene != None:
                self.active_scene = self.active_scene.next

            dt = self.clock.tick(self.fps)/1000.0


def main():
    """
    Initialize; create an App; and start the main loop.
    """
    mode_flags = DOUBLEBUF | OPENGL
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    framerate = ConfigSettings().framerate
    pg.init()
    pg.display.set_caption(ConfigSettings().caption)
    pg.display.set_mode((ConfigSettings().width, ConfigSettings().height), mode_flags)
    App(framerate).main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
