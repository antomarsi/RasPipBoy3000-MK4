import pygame, os, time, math
from pygame.locals import *
from PIL import Image, ImageFilter
from dotenv import load_dotenv
from pathlib import Path

class Engine():

    def __init__(self):
        print ("Initialize pygame")
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)

        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = (int(os.getenv('SCREEN_WIDTH')), int(os.getenv('SCREEN_HEIGHT')))
        print('Size: {0}x{1}'.format(self.size[0], self.size[1]))
        print("(done)")

    def on_init(self):
        print ("on_init()")
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        print("(done)")

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

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
