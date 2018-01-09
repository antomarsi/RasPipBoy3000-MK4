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
        self.blur_cooldown = Unit(random.randint(500,2000))
        self.scanline_effect = Rect(0, 0, config.WIDTH, 0)
        self.background = None

    def drawAll(self):
        top = self.menu.draw_header(self.current_tab, self.tabs)
        self.screen.blit(top, (config.WIDTH*0.05, 0), None, pygame.BLEND_ADD)

        tab = self.tabs[self.current_tab].draw(self.character)
        self.screen.blit(tab, (0, config.HEIGHT*0.15), None, pygame.BLEND_ADD)

        footer = self.tabs[self.current_tab].drawFooter(self.character)
        self.screen.blit(footer, (config.WIDTH*0.05, config.HEIGHT-config.MEDcharHeight-(config.HEIGHT*0.05)), None, pygame.BLEND_ADD)

    def drawOverlay(self):
        scan_lines = self.screen.convert_alpha()
        scan_lines.fill((255, 255, 255, 25))
        for j in range(0, self.screenSize[1], 2):
            scan_lines.fill((0, 0, 0, 75), (0, j, self.screenSize[0], 1), pygame.BLEND_RGBA_MULT)

        self.screen.blit(scan_lines, (0, 0)) 
        self.background = self.screen.convert_alpha()
        self.background.fill((0, 200, 0), None, pygame.BLEND_RGBA_MULT)
        if False:
            if self.scanline_effect.height < 32:
                self.scanline_effect.height += 4
            else:
                self.scanline_effect.y += 4
            if self.scanline_effect.y > config.HEIGHT+32:
                self.scanline_effect.x = 0
                self.scanline_effect.y = 0
                self.scanline_effect.height = 1

            self.background.fill((50, 50, 50, 0), self.scanline_effect, pygame.BLEND_RGBA_SUB)
        self.screen.blit(self.background, (0,0))
            
        if config.POST_PROCESSING:
            ##EFEITO DE GLOW
            self.screen.blit(Effects.blur_surf(self.screen, 1), (0,0), None, pygame.BLEND_ADD)

            #EFEITO DE BLINK
            if (self.blur_cooldown.fire()):
                self.screen.blit(Effects.blur_surf(self.screen, 3), (0,0), None, pygame.BLEND_ADD)
                self.blur_cooldown.cooldown = random.randint(100,1000)

    def run(self):
        # Main Loop
        running = True
        
        while running:
            bg = self.screen.convert()

            bg.fill((0, 0, 0))
            self.screen.blit(bg, (0,0))
            self.drawAll()
            self.drawOverlay()

            pygame.display.flip()
            self.clock.tick(config.FPS)

        pygame.quit()

if __name__ == '__main__': 
    engine = Engine()
    engine.run()