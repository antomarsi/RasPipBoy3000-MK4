import abc, settings, pygame
from classes.interface.MenuInterface import MenuInterface

class TabMenuInterface(MenuInterface):

    @property
    def name(self):
        raise NotImplementedError

    @property
    def surface(self):
        raise NotImplementedError

    def draw_sub_menu_name(self, submenu, margin_left, color):
        text_render = settings.FONT_MD.render(submenu.name, 1, color)
        pygame.draw.rect(self.surface, settings.BACK_COLOR,
            [
                self.margin[0]+margin_left,
                0,
                text_render.get_width(),
                text_render.get_height()
            ])
        self.surface.blit(text_render, [self.margin[0] + margin_left, 0])
        return text_render.get_width() + settings.MD_WIDTH


