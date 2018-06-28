import os, pygame, settings, json
from pygame.locals import *
from classes.utils.Effects import Effects
from classes.interface.TabMenuInterface import TabMenuInterface

class SpecialSubMenu(TabMenuInterface):

    name = "Special"
    surface = None
    selected = 0
    special_info = []

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
        with open(os.getenv('SPECIAL_INFO')) as f:
            self.special_info = json.load(f)

    def prev_special(self):
        self.selected -= 1
        if (self.selected < 0):
            self.selected = len(self.special_info)-1
        return

    def next_special(self):
        self.selected += 1
        if (self.selected >= len(self.special_info)):
            self.selected = 0
        return

    def event(self, event):
        if event.type== pygame.KEYDOWN:
            if event.key == K_KP5:
                self.prev_special()
            elif event.key == K_KP2:
                self.next_special()
        pass

    def process(self):
        pass

    def draw(self):
        self.draw_list(self.selected)
        if (list(self.special_info.values())[self.selected]['description']):
            self.draw_description(list(self.special_info.values())[self.selected]['description'])
        pass

    def draw_list(self, selected):
        Effects.draw_list_selected(self.surface, self.special_info.keys(), (
                settings.DRAW_COLOR,
                settings.DRAW_COLOR,
                settings.BACK_COLOR,
                settings.MID_COLOR
            ), pygame.Rect(
                self.margin[0],
                self.margin[1],
                self.size[0]/2,
                self.size[1]
            ), settings.FONT_MD, selected)
        pass

    def draw_description(self, text):
        rect = (
            self.size[0]/2,
            self.size[1]/2,
            self.size[0]/2 - self.margin[0],
            self.size[1]/2 - self.margin[1]
        )
        pygame.draw.rect(self.surface, settings.MID_COLOR, rect)
        Effects.draw_text(self.surface, text, settings.DRAW_COLOR, rect, settings.FONT_SM, True)
        pass
