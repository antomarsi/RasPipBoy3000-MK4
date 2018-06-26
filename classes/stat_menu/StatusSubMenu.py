import os, pygame, settings, json
from classes.utils.Effects import Effects
from classes.interface.TabMenuInterface import TabMenuInterface

class StatusSubMenu(TabMenuInterface):

    name = "Status"
    surface = None

    def __init__(self):
        print('Initialize StatusSubMenu')
        self.size = (
            int(os.getenv('SCREEN_WIDTH')),
            int(int(os.getenv('SCREEN_HEIGHT'))*0.8)
        )
        self.margin = (self.size[0]*0.02, self.size[1]*0.02)
        self.surface = pygame.Surface(self.size)

        self.load_data()

        print('(done)')

    def load_data(self):
        print('Loading player\'s data...')
        with open(os.getenv('PLAYER_DATA')) as f:
            self.player = json.load(f)

    def event(self, event):
        pass

    def process(self):
        pass

    def draw(self):
        text_render = settings.FONT_MD.render(self.player['name'], 1, settings.DRAW_COLOR)
        self.surface.blit(text_render, (0, 0))
        self.drawConditions()
        pass

    def drawConditions(self):
        Effects.draw_progressbar(self.surface, [100, 100, 100, 10], self.player['bodypartsCond']['H'], 100, settings.DRAW_COLOR)
        pass
