import os, abc, pygame, settings
from classes.interface.TabMenuInterface import TabMenuInterface

class StatusSubMenu(TabMenuInterface):

    name = "Status"
    surface = None

    def __init__(self):
        print('Initialize StatusSubMenu', end='')
        self.size = (
                int(os.getenv('SCREEN_WIDTH')),
                int(int(os.getenv('SCREEN_HEIGHT'))*0.8)
                )
        self.margin = (self.size[0]*0.02, self.size[1]*0.02)
        self.surface = pygame.Surface(self.size)
        print('(done)')

    def event(self, event):
        pass

    def process(self):
        pass

    def draw(self):
        self.surface.fill(settings.DRAW_COLOR)
        pass
