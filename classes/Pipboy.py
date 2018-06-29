import os, abc, pygame, settings
from pygame.locals import *
from classes.interface.MenuInterface import MenuInterface
from classes.utils.Effects import Effects
from classes.utils.Sounds import Sounds

class Pipboy(MenuInterface):

    def __init__(self):
        print('Initialize class PipBoy', end='')
        self.size = settings.SCREEN_SIZE
        self.max_menus = settings.MAX_MENUS

        # margin
        # top, left, right, bottom
        self.margin = (self.size[1]*0.038, self.size[0]*0.025, self.size[0]*0.025, self.size[1]*0.028)

        # create the surface and paint it
        self.surface = pygame.Surface(self.size)
        self.surface.fill(settings.BACK_COLOR)

        # Initialize the Menus
        self.menu_position = (0, int(self.size[1]*0.1))
        self.menus = []
        self.selected_menu = None
        self.selected_menu_index = 0

        self.lines_start = []
        self.lines_end = []

        #play sounds
        if settings.USE_SOUND:
            Sounds.random_up_play()
            Sounds.loop_play()
        print('(done)')

    # Select the previous 
    def prev_menu(self):
        if len(self.menus) == 0:
            raise IndexError
        if self.selected_menu_index > 0:
            self.selected_menu_index -= 1
            self.selected_menu = self.menus[self.selected_menu_index]
        else:
            self.selected_menu_index = len(self.menus)-1
            self.selected_menu = self.menus[self.selected_menu_index]

    def next_menu(self):
        if len(self.menus) == 0:
            raise IndexError
        if len(self.menus) > self.selected_menu_index+1:
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
            if event.key == K_KP1 or event.key == K_j:
                Sounds.play_horizontal()
                self.prev_menu()
            elif event.key == K_KP3 or event.key == K_l:
                Sounds.play_horizontal()
                self.next_menu()
        if (self.selected_menu):
            self.selected_menu.event(event)
        pass

    def process(self):
        pass

    def draw_lines(self):
        lines = [
            [self.margin[1], self.margin[0] + settings.LG_HEIGHT + self.size[1]*0.02],
            [self.margin[1], self.margin[0] + settings.LG_HEIGHT],
            [self.size[0] - self.margin[2], self.margin[0] + settings.LG_HEIGHT],
            [self.size[0] - self.margin[2], self.margin[0] + settings.LG_HEIGHT + self.size[1]*0.02],
        ]
        pygame.draw.lines(self.surface, settings.DRAW_COLOR, False, lines, 4)
        pass

    def draw_menu_title(self, text, order, selected=False):
        text_render = settings.FONT_LG.render(text, 1, settings.DRAW_COLOR)
        text_width = text_render.get_width()
        if order == 0:
            position = (
                self.size[0]*0.148,
                self.margin[0]
            )
            self.padding_menu_left += position[0]
        else:
            self.padding_menu_left += settings.LG_WIDTH
            position = (
                self.padding_menu_left,
                self.margin[0]
            )
        self.padding_menu_left += text_render.get_width() + settings.LG_WIDTH

        if selected:
            pygame.draw.rect(self.surface, settings.BACK_COLOR, [
                position[0]-(settings.LG_WIDTH/2) - 1,
                position[1],
                text_width + settings.LG_WIDTH + 3, text_render.get_height() + self.size[1]*0.02
            ])
            pygame.draw.lines(self.surface, settings.DRAW_COLOR, False, [
                [position[0] - (settings.LG_WIDTH), self.margin[0] + settings.LG_HEIGHT],
                [position[0] - (settings.LG_WIDTH/2), self.margin[0] + settings.LG_HEIGHT],
                [position[0] - (settings.LG_WIDTH/2), self.margin[0] + (settings.LG_HEIGHT/3) ],
                [position[0] - (settings.LG_WIDTH/2) / 4, self.margin[0] + (settings.LG_HEIGHT/3)]
            ], 4)

            pygame.draw.lines(self.surface, settings.DRAW_COLOR, False, [
                [position[0] + text_width + (settings.LG_WIDTH), self.margin[0] + settings.LG_HEIGHT],
                [position[0] + text_width + (settings.LG_WIDTH/2), self.margin[0] + settings.LG_HEIGHT],
                [position[0] + text_width + (settings.LG_WIDTH/2), self.margin[0] + (settings.LG_HEIGHT/3) ],
                [position[0] + text_width + (settings.LG_WIDTH/2) / 4, self.margin[0] + (settings.LG_HEIGHT/3)]
            ], 4)
        self.surface.blit(text_render, position)

    def draw(self):
        i = 0
        pygame.draw.rect(self.surface, settings.BACK_COLOR, [
            0, 0,
            self.size[0],
            self.margin[0] + settings.LG_HEIGHT + self.size[1]*0.02]
        )
        self.padding_menu_left = 0
        self.draw_lines()
        for menu in (self.menus):
            self.draw_menu_title(menu.name, i, menu == self.selected_menu)
            i += 1
        if self.selected_menu:
            self.selected_menu.draw()
            self.surface.blit(self.selected_menu.surface, self.margin[1], self.margin[0] + settings.LG_HEIGHT + self.size[1]*0.02))
