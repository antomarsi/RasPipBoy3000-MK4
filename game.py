import pygame, os, time, math
from pygame.locals import *
from classes.Pipboy import Pipboy
from PIL import Image, ImageFilter
from dotenv import load_dotenv
from pathlib import Path
from scenes.StartScene import StartScene
import settings

class Engine():
    def __init__(self):
        print ('Initialize pygame')
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        self._running = True
        self._display_surf = None
        self._current_scene = None
        self._background = None
        self._transition = False
        self.size = self.width, self.height = (int(os.getenv('SCREEN_WIDTH')), int(os.getenv('SCREEN_HEIGHT')))
        print('(done)')
        print('Size: {0}x{1}'.format(self.size[0], self.size[1]))

    def change_scene(self, classtype):
        module = __import__('scenes.'+classtype, fromlist=[classtype])
        new_scene = getattr(module, classtype)
        self._current_scene = new_scene()

        pass

    def update_screen(self):
        pass

    def on_init(self):
        print ('Start on_init()')
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._background = pygame.Surface(self._display_surf.get_size())
        self._background = self._background.convert()
        self._background.fill(settings.BACK_COLOR)
        self._running = True
        self.clock = pygame.time.Clock()
        print('Starting Start Scene Class:')
        self.change_scene('StartScene')
        print('(done)')

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                self._running = False
            elif event.key == K_q:
                self._running = False
        if self._current_scene is not None:
            self._current_scene.event(event)

    def on_loop(self):
        delta_time = self.clock.get_time()
        if self._current_scene is not None:
            self._current_scene.update(delta_time)

    def on_draw(self):
        self._display_surf.blit(self._background, (0, 0))
        if self._current_scene is not None:
            self._current_scene.draw(self._display_surf)
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
            if self._transition == False:
                self.on_loop()
                self.on_draw()
        self.on_cleanup()

    def run(self):
        self.on_execute()

if __name__ == '__main__':
    engine = Engine()
    engine.run()
