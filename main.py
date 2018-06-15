import pygame, os, time, math
from pygame.locals import *
from classes.Pipboy import Pipboy
from PIL import Image, ImageFilter
from dotenv import load_dotenv
from pathlib import Path
import settings

class Engine():

    def __init__(self):
        print ('Initialize pygame')
        print (settings.DRAW_COLOR)
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)

        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = (int(os.getenv('SCREEN_WIDTH')), int(os.getenv('SCREEN_HEIGHT')))

        print('Configuração')

        print('(done)')
        print('Size: {0}x{1}'.format(self.size[0], self.size[1]))

    def on_init(self):
        print ('Start on_init()', end='')
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.pipboy = Pipboy();
        print('(done)')

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        self.pipboy.event(event)

    def on_loop(self):
        pass

    def on_render(self):
        self.pipboy.draw()
        self.background = self._display_surf.convert_alpha()
        self.background.fill(settings.TINT_COLOR, None, pygame.BLEND_RGBA_MULT)
        self._display_surf.blit(self.background, (0,0))
        pygame.display.flip()

    def on_cleanup(self):
        print('Start cleanup', end='')
        pygame.quit()
        print('(done)')

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
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
