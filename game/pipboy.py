import pygame as pg
from pygame.locals import *
from game.modules.stats import StatsModule
from game.ui import Header, Overlay, Scanlines
from utils.shaders import Shader
from utils.config import config
from utils.scanline_gradient import ScanLineGradient
from core.resource_loader import ResourceLoader
from core.engine import Engine
from utils.logger import logger

if config.GPIO_AVALIABLE:
    import RPi.GPIO as GPIO  # type: ignore


class PipBoy(Engine):

    def __init__(self, framerate=60, *args, **kwargs):
        logger.debug("Initializing PipBoy Engine")
        super().__init__(*args, **kwargs)
        # self.screen = pg.Surface(self.config.SIZE).convert(
        #     (16711680, 65280, 255, 0), 0)
        # self.display_screen = pg.Surface(self.config.DISPLAY_SIZE).convert(
        #     (16711680, 65280, 255, 0), 0)
        # self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.framerate = framerate
        self.active = None

        self.init_fonts()
        self.init_children()
        self.init_modules()

        self.gpio_actions = {}
        if config.GPIO_AVALIABLE:
            self.init_gpio_controls()


        # self.shader = Shader(self.display_screen,
        #                      self.config.USE_SCANLINE, self.config.TINT_COLOR)
        # self.font = pg.font.Font(None, 30)
        # self.show_fps = False
        # self.sprite_list = pg.sprite.LayeredDirty((ScanLineGradient()))

    def init_fonts(self):
        pg.font.init()
        for size in [41]:
            ResourceLoader.getInstance().add_font("ROBOTO_B", "RobotoCondensed-Bold.ttf", size)
            ResourceLoader.getInstance().add_font("ROBOTO", "RobotoCondensed-Regular.ttf", size)
            ResourceLoader.getInstance().add_font("TECHMONO", "TechMono.ttf", size)


    def init_children(self):
        ResourceLoader.getInstance().add_image("scanline", "images/overlay.png")
        overlay = Overlay()
        # self.root_children.add(overlay)
        ResourceLoader.getInstance().add_image("scanline", "images/scanline.png")
        scanlines = Scanlines()
        # self.root_children.add(scanlines)


    def init_modules(self):
        self.modules = [
            StatsModule(self)
        ]
        self.header = Header(options=self.modules)
        self.root_children.add(self.header)
        self.active = self.modules[0]
        self.add(self.active)

    def switch_module(self, module_index):
        if module_index < len(self.modules):
            if self.active:
                self.active.handle_pause()
                self.remove(self.active)
            self.active = self.modules[module_index]
            self.add(self.active)
            self.active.handle_resume()
        else:
            raise Exception(f"Module {module_index} not implemented")


    def init_gpio_controls(self):
        for pin in config.GPIO_ACTIONS.keys():
            logger.info(
                f"Initializing pin {pin} as action '{config.GPIO_ACTIONS[pin]}'")
            GPIO.setup(pin, GPIO.IN)
            self.gpio_actions[pin] = config.GPIO_ACTIONS[pin]

    def check_gpio_input(self):
        for pin in self.gpio_actions.keys():
            if not GPIO.input(pin):
                self.handle_action(self.gpio_actions[pin])

    def handle_action(self, action):
        if action.startswitch('module_'):
            self.switch_module(action[7:])
        else:
            if self.active:
                self.active.handle_action(action)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.running = False
            elif event.key in config.ACTIONS:
                self.handle_action(config.ACTIONS[event.key])
        elif event.type == pg.QUIT:
            self.running = False
        # elif event.type == config.EVENTS['SONG_END']
        else:
            if self.active:
                self.active.handle_event(event)

    def update(self):
        if self.active:
            self.active.update()
        super().update()

    def render(self, deltatime):
        super().render(deltatime)
        if self.active:
            self.active.render(deltatime)

        # """
        # Render all needed elements and update the display.
        # """
        # self.screen.fill(self.config.BG_COLOR)

        # if self.main_scene != None:
        #     self.main_scene.render(self.screen)
        # self.sprite_list.draw(self.screen)

        # if self.show_fps:
        #     self.screen.blit(self.font.render(
        #         str(int(self.clock.get_fps())), True, pg.Color('white')), (10, 10))
        # scaled_screen = pg.transform.smoothscale(
        #     self.screen, self.display_screen.get_size())
        # self.display_screen.blit(scaled_screen, (0, 0))
        # self.shader.render(self.display_screen)
        # pg.display.flip()

    def run(self):
        self.running = True
        while self.running:
            deltatime = self.clock.tick(10) / 1000 * self.framerate
            for event in pg.event.get():
                self.handle_event(event)
            self.update()
            self.render(deltatime)
            self.check_gpio_input()
        try:
            pg.mixer.quit()
        except:
            pass
