import os, abc, pygame, settings
from classes.interface.TabMenuInterface import TabMenuInterface
from classes.utils.Effects import Effects

class StatMenu(TabMenuInterface):

    name = 'Stat'
    surface = None

    def __init__(self):
        print('Initialize tab Stat', end='')
        self.size = (int(os.getenv('SCREEN_WIDTH')), int(int(os.getenv('SCREEN_HEIGHT'))*0.9))
        self.margin = (self.size[0]*0.02, self.size[1]*0.02)
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

    def draw_bottom(self):
        size = (self.size[0]-(self.margin[0]*2), settings.SM_HEIGHT)
        one_slice_width = size[0] / 4
        pos_y = self.size[1]-((settings.SM_HEIGHT)*2)-self.margin[1]
        # DRAW HP - LEFT BAR
        pygame.draw.rect (self.surface, settings.MID_COLOR, [self.margin[0], pos_y, one_slice_width, size[1]])
        text_render = settings.FONT_SM.render('HP: 100/100', 1, settings.DRAW_COLOR)
        self.surface.blit(text_render, [self.margin[0]+settings.SM_WIDTH, pos_y])
        # DRAW XP - MID BAR
        pygame.draw.rect(self.surface, settings.MID_COLOR, [self.margin[0]+one_slice_width+settings.SM_WIDTH, pos_y, (one_slice_width*2)-settings.SM_WIDTH*2, size[1]])
        text_render = settings.FONT_SM.render('LEVEL: 1', 1, settings.DRAW_COLOR)
        self.surface.blit(text_render, [self.margin[0]+one_slice_width+settings.SM_WIDTH*2, pos_y])
        Effects.draw_progressbar(self.surface, [
            self.margin[0]+one_slice_width+(settings.SM_WIDTH*2)+text_render.get_width(),
            pos_y+settings.SM_HEIGHT*0.1,
            (one_slice_width*2)-text_render.get_width()-(settings.SM_WIDTH*4),
            settings.SM_HEIGHT*0.8
            ], 80, 100, settings.DRAW_COLOR)
        # DRAW 3rd  RIGHT BAR
        pygame.draw.rect (self.surface, settings.MID_COLOR, [self.size[0]-self.margin[0]-one_slice_width, pos_y, one_slice_width, size[1]])
        text_render = settings.FONT_SM.render('AP: 100', 1, settings.DRAW_COLOR)
        self.surface.blit(text_render, [self.size[0]-self.margin[0]-text_render.get_width()-settings.SM_WIDTH, pos_y])
        #pygame.draw.rect(self.surface, settings.MID_COLOR, [self.margin[0], self.size[1]-settings.MD_HEIGHT*2, size[0], size[1]])

    def process(self):
        pass

    def draw(self):
        self.draw_bottom()
        for menu in (self.menus):
            pass
        if self.selected_menu:
            self.selected_menu.draw()
            self.surface.blit(self.selected_menu.surface, self.sub_menu_position)
        pass
