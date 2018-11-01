import settings, pygame
from pygame.locals import *
from gui.GuiScreen import GuiScreen
from gui.GuiLabel import GuiLabel
from gui.GuiFillLabel import GuiFillLabel, Alignment
from gui.GuiSprite import GuiSprite
from gui.GuiFillBar import GuiFillBar

class StartScene(GuiScreen):

    def __init__(self):
        super(StartScene, self).__init__()
        self.make_gui()

    def make_gui(self):
        size = pygame.display.get_surface().get_size()
        newSize = self.scale(1280, 720, 1280, size[1])
        bg = GuiSprite(settings.ROOT_DIR+'/assets/temp/menu1.png', position = (-95, 0) , scale = newSize)
        self.add_element(0, bg)
        texto_teste = GuiLabel('texto_teste', settings.FONT_LG, color=(250, 250, 250), position=(200, 50), bgcolor=(200,0,0))
        #self.add_element(1, texto_teste)

        self.hp_text = GuiFillLabel('HP115/115', settings.FONT_SM, (19, 316, 96, 20), margin = (5, 0), color=(255, 255, 255), bgcolor=(128, 128, 128))
        self.add_element(2, self.hp_text)

        self.ap_text = GuiFillLabel('AP90/90', settings.FONT_SM, (321, 316, 96, 20), margin = (5, 0), color=(255, 255, 255), bgcolor=(128, 128, 128), alignment=Alignment.RIGHT)
        self.add_element(3, self.ap_text)

        self.level_text = GuiFillLabel('LEVEL6', settings.FONT_SM, (118, 316, 200, 20), margin = (5, 0), color=(255, 255, 255), bgcolor=(128, 128, 128))
        self.add_element(4, self.level_text)

        self.exp_bar = GuiFillBar(color = (255, 255, 255), rect = (172, 320, 138, 11), line_width = 1, max_value = 10, value = 3)
        self.add_element(5, self.exp_bar)

    def scale(self, w, h, x, y, maximum=True):
        nw = y * w / h
        nh = x * h / w
        if maximum ^ (nw >= x):
                return int(nw) or 1, int(y)
        return int(x), int(nh) or 1

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_d:
                self.ap_text.visible = not self.ap_text.visible
            if event.key == K_RIGHT:
                self.bar.set_value(self.exp_bar.value + 1)
