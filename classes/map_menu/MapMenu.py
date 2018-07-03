import os, abc, pygame, settings
from classes.interface.TabMenuInterface import TabMenuInterface

class DataMenu(TabMenuInterface):

    name = 'Map'
    surface = None

    def __init__(self):
        print('Initialize tab Data', end='')
        self.size = (int(os.getenv('SCREEN_WIDTH')), int(int(os.getenv('SCREEN_HEIGHT'))*0.9))
        self.surface = pygame.Surface(self.size)
        self.sub_menu_position = (0, int(self.size[1]*0.1))
        self.menus = []
        self.selected_menu = None
        self.selected_menu_index = 0
        print('(done)')

    def prev_sub_menu(self):
        if len(self.menus) == 0:
            raise IndexError
        if self.selected_menu_index-1 >= 0:
            self.selected_menu_index -= 1
            self.selected_menu = self.menus[self.selected_menu_index]
        else:
            self.selected_menu_index = len(self.selected_menu)-1
            self.selected_menu = self.menus[self.selected_menu_index]

    def next_sub_menu(self):
        if len(self.menus) == 0:
            raise IndexError
        if len(self.menus) <= self.selected_menu_index+1:
            self.selected_menu_index += 1
            self.selected_menu = self.menus[self.selected_menu_index]
        else:
            self.selected_menu_index = 0
            self.selected_menu = self.menus[self.selected_menu_index]

    def add_sub_menu(self, menu):
        self.menus.append(menu)
        if self.selected_menu == None:
            self.selected_menu = self.menus[0]

    def event(self, event):
        pass

    def process(self):
        pass

    def draw(self):
        self.surface.fill((255,255,255))
        for menu in (self.menus):
            pass
        if self.selected_menu:
            self.selected_menu.draw()
            self.surface.blit(self.selected_menu.surface, self.sub_menu_position)
        pass
