import pygame as pg
from pygame.locals import *
from game.data.player import PlayerStatus
from game.modules import stat, inv, data, radio, map as pipmap, boot
from game.ui import Overlay, ReferenceImage, Scanlines
from utils.settings import config
from core.resource_loader import ResourceLoader
from core.engine import Engine, EntityGroup
from utils.logger import logger

if config.GPIO_AVALIABLE:
    import RPi.GPIO as GPIO  # type: ignore


class PipBoy(Engine):
    current_submodule = 0
    modules = {}

    def __init__(self, framerate=30, *args, **kwargs):
        logger.debug("Initializing PipBoy Engine")
        super().__init__(*args, **kwargs)
        self.clock = pg.time.Clock()
        self.framerate = framerate
        self.active = None

        self.init_fonts()
        self.init_children()
        self.init_modules()

        self.gpio_actions = {}
        if config.GPIO_AVALIABLE:
            self.init_gpio_controls()

    def init_fonts(self):
        logger.debug("Initializing fonts")
        pg.font.init()
        for size in [12, 24, 30, 41]:
            ResourceLoader.add_font(
                "MONOFONTO", "fonts/monofonto.ttf", size)
            ResourceLoader.add_font(
                "ROBOTO_B", "fonts/RobotoCondensed-Bold.ttf", size)
            ResourceLoader.add_font(
                "ROBOTO", "fonts/RobotoCondensed-Regular.ttf", size)
            ResourceLoader.add_font("TECHMONO", "fonts/TechMono.ttf", size)
        logger.debug("Fonts initialized")

    def init_children(self):
        logger.debug("Initializing childs")

        self.foregroundGroup = EntityGroup()
        self.scanlines = Scanlines()
        self.overlay = Overlay()
        self.debug_image = ReferenceImage(self.screen)
        self.debug_image.visible = False
        self.add(self.overlay)
        self.add(self.scanlines)
        self.add(self.debug_image)
        logger.debug("Childs initialized")

    def init_full_modules(self):
        self.modules["inv"] = inv.Module(self)
        self.modules["stat"] = stat.Module(self)
        self.modules["map"] = pipmap.Module(self)
        self.modules["radio"] = radio.Module(self)
        self.modules["data"] = data.Module(self)

    def init_modules(self):
        global playerStatus
        logger.debug("Initializing Modules")
        self.modules = {
            "boot": boot.Module(self)
        }
        playerStatus = PlayerStatus()
        self.init_full_modules()

        self.switch_module("map")

    def switch_module(self, module):
        if module in self.modules:
            if self.active:
                self.active.handle_action("pause")
                self.remove(self.active)
            self.active = self.modules[module]
            self.active.parent = self
            self.active.handle_resume()
            self.add(self.active)
        else:
            raise Exception(f"Module {module} not implemented")

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
        if action.startswith('module_'):
            self.switch_module(action[7:])
        else:
            if self.active:
                self.active.handle_action(action)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.running = False
            elif event.key == pg.K_h:
                self.debug_image.visible = not self.debug_image.visible
            elif event.key in config.ACTIONS:
                self.handle_action(config.ACTIONS[event.key])
        elif event.type == pg.QUIT:
            self.running = False
        # elif event.type == config.EVENTS['SONG_END']
        if self.active and self.running:
            self.active.handle_event(event)

    def update(self, deltatime):
        if self.active and self.running:
            self.active.update(deltatime)
        return super().update(deltatime)

    def run(self):
        self.running = True
        while self.running:
            deltatime = self.clock.tick(self.framerate) / 1000
            for event in pg.event.get():
                self.handle_event(event)
            self.update(deltatime)
            self.render()
            self.check_gpio_input()
        try:
            pg.mixer.quit()
        except:
            pass
