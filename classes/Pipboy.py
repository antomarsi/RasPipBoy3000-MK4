import os, abc, pygame, settings
from classes.MenuInterface import MenuInterface

class Pipboy(MenuInterface):

    def __init__(self):
        print('Initialize class PipBoy', end='')
        self.size = (int(os.getenv('SCREEN_WIDTH')), int(os.getenv('SCREEN_HEIGHT')))
        self.screen = pygame.display.set_mode(self.size)
        self.menus = []
        print('(done)')

    def addMenu(self, menu):
        self.menus.append(menu)

    def event(self, event):
        return

    def process(self):
        return

    def draw_lines(self):
        pygame.draw.lines(self.screen, settings.DRAW_COLOR, False, [
            [self.size[0] * 0.02, self.size[1]*0.1],
            [self.size[0] * 0.02, self.size[1]*0.06],
            [self.size[0] - (self.size[0] * 0.02), self.size[1]*0.06],
            [self.size[0] - (self.size[0] * 0.02), self.size[1]*0.1],
        ], 2)
        pass

    def draw(self):
        self.draw_lines()
        for menu in (self.menus):
            textImg = config.FONT_LRG.render(tabs[tabNum].tabName, True, config.DRAWCOLOUR)
            TextWidth = (textImg.get_width())
            topPad = self.size_header_y-textImg.get_height()*1.5
            TextX = ((SpacingX*tabNum) + (TextWidth / len_tab-1)) + SpacingX*0.5
            textPos = (TextX, topPad)
            pass
        return
