import os, abc, pygame, settings
from pygame.locals import *
from classes.interface.MenuInterface import MenuInterface
from classes.utils.Effects import Effects

class Pipboy(MenuInterface):

    def __init__(self):
        print('Initialize class PipBoy', end='')
        self.size = settings.SCREEN_SIZE
        self.max_menus = settings.MAX_MENUS

        self.margin = (self.size[0]*0.1, self.size[1]*0.08)
        self.padding_menu = ((int(self.size[0]-(self.margin[1]*2))/self.max_menus), 0)

        self.menu_position = (0, int(self.size[1]*0.15))
        self.surface = pygame.Surface(self.size)
        self.menus = []
        self.selected_menu = None
        self.selected_menu_index = 0
        print('(done)')

    def prev_menu(self):
        if len(self.menus) == 0:
            raise IndexError
        if self.selected_menu_index-1 >= 0:
            self.selected_menu_index -= 1
            self.selected_menu = self.menus[self.selected_menu_index]
        else:
            self.selected_menu_index = len(self.menus)-1
            self.selected_menu = self.menus[self.selected_menu_index]

    def next_menu(self):
        if len(self.menus) == 0:
            raise IndexError
        if len(self.menus) < self.selected_menu_index:
            self.selected_menu_index += 1
            self.selected_menu = self.menus[self.selected_menu_index]
        else:
            self.selected_menu_index = 0
            self.selected_menu = self.menus[self.selected_menu_index]

    def add_menu(self, menu):
        self.menus.append(menu)
        if self.selected_menu == None:
            self.selected_menu = self.menus[0]

    def event(self, event):
        if event.type== pygame.KEYDOWN:
            if event.key == K_KP1:
                self.prev_menu()
            elif event.key == K_KP3:
                self.next_menu()
        if (self.selected_menu):
            self.selected_menu.event(event)
        pass

    def process(self):
        pass

    def draw_lines(self):
        lines_start = [
            [self.size[0] * 0.02, self.size[1]*0.12],
            [self.size[0] * 0.02, self.size[1]*0.08]
        ] + self.lines_start

        lines_end = self.lines_end + [
            [self.size[0] - (self.size[0] * 0.02), self.size[1]*0.08],
            [self.size[0] - (self.size[0] * 0.02), self.size[1]*0.12]
        ]
        pygame.draw.lines(self.surface, settings.DRAW_COLOR, False, lines_start, 1)
        pygame.draw.lines(self.surface, settings.DRAW_COLOR, False, lines_end, 1)
        pass

    def draw_menu_title(self, text, order, selected=False):
        print('printing '+text+' at '+ str(order))
        text_render = settings.FONT_LG.render(text, 1, settings.DRAW_COLOR)
        text_width = text_render.get_width()
        text_height = text_render.get_height()
        position = (
            self.margin[0] + (self.padding_menu[0] * order),
            self.margin[1] + (self.padding_menu[1] * order) - (text_height * 0.8)
        )
        pygame.draw.rect(self.surface, settings.BACK_COLOR, [
            position[0] - settings.LG_WIDTH,
            position[1],
            text_width + settings.LG_WIDTH * 2, text_render.get_height()
        ])
        if selected:
            self.lines_start = [
                [position[0] - settings.LG_WIDTH, self.size[1] * 0.08],
                [position[0] - settings.LG_WIDTH, self.size[1] * 0.06],
                [position[0] - settings.LG_WIDTH / 4, self.size[1] * 0.06]
            ]
            self.lines_end = [
                [position[0] + text_width + settings.LG_WIDTH / 4, self.size[1] * 0.06],
                [position[0] + text_width + settings.LG_WIDTH, self.size[1] * 0.06],
                [position[0] + text_width + settings.LG_WIDTH, self.size[1] * 0.08]
            ]
        self.surface.blit(text_render, position)

    def draw(self):
        i = 0
        for menu in (self.menus):
            self.draw_menu_title(menu.name, i, menu == self.selected_menu)
            i += 1
        self.draw_lines()
        if self.selected_menu:
            self.selected_menu.draw()
            self.surface.blit(self.selected_menu.surface, (self.menu_position))
