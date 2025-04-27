import pygame as pg
from pygame.locals import *
from game.modules import stats, inv
from game.ui import Header, Overlay, Scanlines
from utils.config import config
from core.resource_loader import ResourceLoader
from core.engine import Engine
from utils.logger import logger

if config.GPIO_AVALIABLE:
    import RPi.GPIO as GPIO  # type: ignore


class PipBoy(Engine):
    current_submodule = 0

    def __init__(self, framerate=60, *args, **kwargs):
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
        for size in [41]:
            ResourceLoader.add_font("ROBOTO_B", "fonts/RobotoCondensed-Bold.ttf", size)
            ResourceLoader.add_font("ROBOTO", "fonts/RobotoCondensed-Regular.ttf", size)
            ResourceLoader.add_font("TECHMONO", "fonts/TechMono.ttf", size)
        logger.debug("Fonts initialized")


    def init_children(self):
        logger.debug("Initializing childs")
        overlay = Overlay()
        self.root_children.add(overlay)
        scanlines = Scanlines()
        self.root_children.add(scanlines)
        logger.debug("Childs initialized")


    def init_modules(self):
        logger.debug("Initializing Modules")
        self.modules = {
            "stats": stats.Module(self),
            "inv": inv.Module(self)
        }
        self.header = Header(options=self.modules.values())

        self.root_children.add(self.header)

        self.switch_module("stats")
        logger.debug("Modules initialized")

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
            for idx, name in enumerate(self.modules):
                if str(name).lower() == action[7:]:
                    self.switch_module(idx)
        else:
            if self.active:
                self.active.handle_action(action)

    def handle_event(self, event):
        super().handle_event(event)
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

    def update(self, deltatime=0):
        if self.active:
            self.active.update()
        super().update(deltatime)

    def render(self):
        super().render()
        if self.active:
            self.active.render()

    def run(self):
        self.running = True
        while self.running:
            deltatime = self.clock.tick(10) / 1000 * self.framerate
            for event in pg.event.get():
                self.handle_event(event)
            self.update(deltatime)
            self.render()
            self.check_gpio_input()
        try:
            pg.mixer.quit()
        except:
            pass
