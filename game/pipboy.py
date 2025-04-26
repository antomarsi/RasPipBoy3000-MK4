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
        pg.font.init()
        for size in [41]:
            ResourceLoader.getInstance().add_font("ROBOTO_B", "RobotoCondensed-Bold.ttf", size)
            ResourceLoader.getInstance().add_font("ROBOTO", "RobotoCondensed-Regular.ttf", size)
            ResourceLoader.getInstance().add_font("TECHMONO", "TechMono.ttf", size)


    def init_children(self):
        ResourceLoader.getInstance().add_image("overlay", "images/overlay.png")
        overlay = Overlay()
        self.root_children.add(overlay)
        ResourceLoader.getInstance().add_image("scanline", "images/scanline.png")
        scanlines = Scanlines()
        self.root_children.add(scanlines)


    def init_modules(self):
        self.modules = {
            "stats": stats.Module(self),
            "inv": inv.Module(self)
        }
        self.header = Header(options=self.modules.values())

        self.root_children.add(self.header)

        self.switch_module("stats")

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
            self.update(deltatime)
            self.render()
            self.check_gpio_input()
        try:
            pg.mixer.quit()
        except:
            pass
