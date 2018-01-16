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
    torchMode = False
    blurimage = None
    glowimage = None
    scan_lines = None
    changed = True
    changedMenu = False
    changedSubMenu = False
    top = menu = submenu = footer = tab = None
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

        if config.USE_SOUND:
            random.choice(config.NEW_SOUNDS['Up']).play()
            self.humSound = config.NEW_SOUNDS["Loop"]
            self.humSound.play(loops=-1)
            self.humVolume = self.humSound.get_volume()

    def drawAll(self):

        if not self.top or self.changedMenu:
            self.top = self.menu.draw_header(self.current_tab, self.tabs)
        self.screen.blit(self.top, (config.WIDTH*0.05, 0), None, pygame.BLEND_ADD)

        if not self.submenu or self.changedSubMenu:
           self.submenu = self.tabs[self.current_tab].draw_submenus()
        self.screen.blit(self.submenu, (config.WIDTH*0.05+10, config.HEIGHT*0.1), None, pygame.BLEND_ADD)

        self.tab = self.tabs[self.current_tab].draw(self.character)
        self.screen.blit(self.tab, (0, config.HEIGHT*0.2), None, pygame.BLEND_ADD)

        if not self.footer or (self.changedMenu or self.changedSubMenu or self.character.changed):
            self.footer = self.tabs[self.current_tab].drawFooter(self.character)
        self.screen.blit(self.footer, (config.WIDTH*0.05, config.HEIGHT-config.MEDcharHeight-(config.HEIGHT*0.05)), None, pygame.BLEND_ADD)


    def drawOverlay(self):
        self.background = self.screen.convert_alpha()
        self.background.fill((0, 200, 0), None, pygame.BLEND_RGBA_MULT)
        self.screen.blit(self.background, (0,0))

        if not self.scan_lines or self.changed:
            self.scan_lines = self.screen.convert_alpha()
            for j in range(0, self.screenSize[1], 2):
                pygame.draw.line(self.scan_lines, (0, 0, 0, 25), (0, j), (self.screenSize[0], j), 1)
        self.screen.blit(self.scan_lines, (0, 0))

        if False:
            if self.scanline_effect.height < 32:
                self.scanline_effect.height += 4
            else:
                self.scanline_effect.y += 4
            if self.scanline_effect.y > config.HEIGHT+32:
                self.scanline_effect.x = 0
                self.scanline_effect.y = 0
                self.scanline_effect.height = 1
            
        if config.POST_PROCESSING:

            #EFEITO DE BLINK
            if (self.blur_cooldown.fire()) and config.BLINK:
                if not self.blurimage:
                    self.blurimage = Effects.blur_surf(self.screen, 4)
                    self.blurimage.set_alpha(128)
                self.screen.blit(self.blurimage, (0,0), None, pygame.BLEND_RGBA_ADD)
                self.blur_cooldown.cooldown = random.randint(500,1000)

            ##EFEITO DE GLOW
            if not self.glowimage or self.changed:
                self.glowimage = Effects.blur_surf(self.screen, 1)
            self.screen.blit(self.glowimage, (0,0), None, pygame.BLEND_RGB_ADD)

    def inputs(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in config.KEYS.values():
                self.changed = True
                if event.key == config.KEYS['PREVIUS_MENU']:
                    if self.menuNum > 0:
                        self.menuNum -= 1
                        config.NEW_SOUNDS['RotaryHorizontal'][0].play()
                if event.key == config.KEYS['NEXT_MENU']:
                    if self.menuNum < len(self.tabs)-1:
                        self.menuNum += 1
                        config.NEW_SOUNDS['RotaryHorizontal'][1].play()                        
                if event.key == config.KEYS['PREVIUS_SUB']:
                    self.tabs[self.menuNum].prev_sub()
                    self.changedSubMenu = True
                    config.NEW_SOUNDS['RotaryHorizontal'][0].play()
                if event.key == config.KEYS['NEXT_SUB']:
                    self.tabs[self.menuNum].next_sub()
                    self.changedSubMenu = True
                    config.NEW_SOUNDS['RotaryHorizontal'][1].play()
                if event.key == config.KEYS['QUIT']:
                    pygame.quit()
        return events

    def run(self):
        # Main Loop
        running = True
        while running:
            events = self.inputs()
            self.tabs[self.current_tab].inputs(events)
            bg = self.screen.convert()

            bg.fill((0, 0, 0))
            self.screen.blit(bg, (0,0))
            self.drawAll()
            self.drawOverlay()
            pygame.display.flip()
            self.clock.tick(config.FPS)

            self.character.changed = False
            self.changed = False
            self.changedMenu = False
            self.changedSubMenu = False
        pygame.quit()

if __name__ == '__main__': 
    engine = Engine()
    engine.run()