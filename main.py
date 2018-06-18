import pygame, os, time, math
from pygame.locals import *
from classes.Pipboy import Pipboy
from classes.StatMenu import StatMenu
from classes.InvMenu import InvMenu
from classes.DataMenu import DataMenu
from PIL import Image, ImageFilter
from dotenv import load_dotenv
from pathlib import Path
import settings

class Engine():

    def __init__(self):
        print ('Initialize pygame')
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)

        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = (int(os.getenv('SCREEN_WIDTH')), int(os.getenv('SCREEN_HEIGHT')))

        print('(done)')
        print('Size: {0}x{1}'.format(self.size[0], self.size[1]))

    def on_init(self):
        print ('Start on_init()')
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.clock = pygame.time.Clock()

        print('Starting PipBoy Class:')
        self.pipboy = Pipboy();
        print('(done)')

        print('Adding Menu: Stat')
        stat_menu = StatMenu()
        self.pipboy.add_menu(stat_menu)
        print('(done)')
        print('Adding Menu: Inv')
        inv_menu = InvMenu()
        self.pipboy.add_menu(inv_menu)
        print('(done)')
        print('Adding Menu: Data')
        data_menu = DataMenu()
        self.pipboy.add_menu(data_menu)
        print('(done)')
        print('on_init: (done)')

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                self._running = False
            elif event.key == K_q:
                self._running = False
        self.pipboy.event(event)

    def on_loop(self):
        pass

    def draw_overlay(self):
        self.background = self._display_surf.convert_alpha()
        self.background.fill(settings.TINT_COLOR, None, pygame.BLEND_RGBA_MULT)
        self._display_surf.blit(self.background, (0,0))

    def on_render(self):
        self.pipboy.draw()
        self._display_surf.blit(self.pipboy.surface, (0, 0))
        self.draw_overlay()
        pygame.display.flip()

    def on_cleanup(self):
        print('Start cleanup', end='')
        pygame.quit()
        print('(done)')

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            self.clock.tick(15)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def run(self):
        self.on_execute()

if __name__ == '__main__':
    engine = Engine()
    engine.run()
