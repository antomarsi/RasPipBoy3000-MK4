import pygame, os, time, random, math, datetime
from pygame.locals import *
from PIL import Image, ImageFilter
import config_new as config
from classes.render.Menu import *
from classes.render.Tabs import *
from classes.render.effects import Effects, Unit
from classes.VaultDweller import VaultDweller

class Engine():

    menuNum = 0
    subMenuNum = 0
    torchMode = False
    background = False

    def __init__(self, *args, **kwargs):

        if(config.USE_SERIAL):
            self.ser = config.ser
            True#self.ser.write("gaugeMode=2")

        print ("Init pygame:")
        pygame.init()
        pygame.display.init()
        print ("(done)")

        self.rootParent = self
        self.screenSize = (config.WIDTH, config.HEIGHT)
        self.canvasSize = (config.WIDTH, config.HEIGHT)

        print('Resolution: {0}x{1}'.format(self.screenSize[0], self.screenSize[1]))
        print('Canvas Size: {0}x{1}'.format(self.canvasSize[0], self.canvasSize[1]))

        pygame.mouse.set_visible(0)
        self.screen = pygame.display.set_mode(self.screenSize, pygame.DOUBLEBUF)

        pygame.event.set_blocked(None)
        for ev in (QUIT, KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN):
            pygame.event.set_allowed(ev)

        self.clock = pygame.time.Clock()
        self.menu = Menu()
        self.tabs = [TabStat(), TabInv(), TabData(), TabMap(), TabRadio()]
        self.current_tab = 0
        self.character = VaultDweller().load()

    def drawAll(self):
        top = self.menu.draw_header(self.current_tab, self.tabs)
        self.screen.blit(top, (config.WIDTH*0.05, 0), None, pygame.BLEND_ADD)
        footer = self.tabs[self.current_tab].drawFooter(self.character)
        self.screen.blit(footer, (config.WIDTH*0.05, config.HEIGHT-config.MEDcharHeight-(config.HEIGHT*0.05)), None, pygame.BLEND_ADD)


    def run(self):
        # Main Loop
        running = True
        blur_cooldown = Unit(random.randint(500,2000))
        while running:
            bg = self.screen.convert()

            bg.fill((0, 0, 0))

            self.screen.blit(bg, (0,0))
            image = config.IMAGES["statusboy"]
            imageSize = config.HEIGHT
            image = pygame.transform.smoothscale(image, (imageSize, imageSize))
            self.screen.blit(image, (((config.WIDTH - imageSize) / 2), 0))

            scan_lines = pygame.Surface(self.screenSize).convert_alpha()
            scan_lines.fill((255, 255, 255, 25))
            for j in range(0, self.screenSize[1], 2):
                scan_lines.fill((0, 0, 0, 75), (0, j, self.screenSize[0], 1), pygame.BLEND_RGBA_MULT)
            self.screen.blit(scan_lines, (0,0))

            self.drawAll()
            #POST_PROCESSING
            #turn everything green
            if not self.background:
                self.background = self.screen.convert()
                self.background.fill((0, 200, 0), None, pygame.BLEND_RGBA_MULT)
            self.screen.blit(self.background, (0,0))

            if config.POST_PROCESSING:
                ##EFEITO DE GLOW
                self.screen.blit(Effects.blur_surf(self.screen, 3), (0,0), None, pygame.BLEND_ADD)

                #EFEITO DE BLINK
                if (blur_cooldown.fire()):
                    self.screen.blit(Effects.blur_surf(self.screen, 1), (0,0))
                    blur_cooldown.cooldown = random.randint(100,1000)

            pygame.display.update()
            self.clock.tick(config.FPS)

        pygame.quit()

if __name__ == '__main__': 
    engine = Engine()
    engine.run()