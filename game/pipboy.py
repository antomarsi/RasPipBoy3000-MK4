import esper
import pygame as pg
from pygame.locals import *
from game.data.store import save_data, save_save
from game.modules import registry
from utils.settings import config
from utils.layout import scale_surface_keep_aspect
from core.components import Active, AutoScroll, Dirty, Layer, Position, Renderable
from core.resource_loader import ResourceLoader
from core.engine import Engine
from utils.logger import logger

if config.GPIO_AVAILABLE:
    import RPi.GPIO as GPIO  # type: ignore

AUTOSAVE_INTERVAL = 30.0
IDLE_THRESHOLD_TICKS = 30  # frames with nothing dirty before dropping to IDLE_FRAMERATE


class PipBoy(Engine):

    def __init__(self, framerate=30, *args, **kwargs):
        logger.debug("Initializing PipBoy Engine")
        super().__init__(*args, **kwargs)
        self.clock = pg.time.Clock()
        self.framerate = framerate
        self._time_since_save = 0.0
        self._idle_ticks = 0

        self.init_fonts()
        self.init_children()
        self.init_modules()

        self.gpio_actions = {}
        if config.GPIO_AVAILABLE:
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

        scanline_image = ResourceLoader.add_image(
            "scanline", "images/scanline.png")
        self.scanline_entity = esper.create_entity(
            Position(0, -130),
            Renderable(image=scanline_image),
            Layer(11),
            Dirty(2),
            AutoScroll(speed=100.0, min_y=-130.0,
                       max_y=self.screen.get_height() + 130.0),
            Active(),
        )

        overlay_image = ResourceLoader.add_image(
            "overlay", "images/overlay.png")
        self.overlay_entity = esper.create_entity(
            Position(0, 0),
            Renderable(image=overlay_image),
            Layer(10),
            Dirty(1),
            Active(),
        )

        debug_raw = ResourceLoader.add_image("debug", "../temp/menu1.png")
        debug_image = scale_surface_keep_aspect(
            debug_raw, None, self.screen.get_height() + 8)
        debug_x = (self.screen.get_width() - debug_image.get_width()) / 2
        self.debug_entity = esper.create_entity(
            Position(debug_x, 0),
            Renderable(image=debug_image, visible=False),
            Layer(0),
            Dirty(1),
            Active(),
        )
        logger.debug("Childs initialized")

    def init_modules(self):
        registry.init_modules(self)
        registry.switch_module(config.STARTUP_MODULE)

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
        registry.handle_action(action)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.running = False
            elif event.key == pg.K_h:
                debug_renderable = esper.component_for_entity(
                    self.debug_entity, Renderable)
                debug_renderable.visible = not debug_renderable.visible
            elif event.key in config.ACTIONS:
                self.handle_action(config.ACTIONS[event.key])
        elif event.type == pg.QUIT:
            self.running = False

    def run(self):
        self.running = True
        while self.running:
            # Battery: while nothing's changed on screen for a while, drop to
            # IDLE_FRAMERATE and actually block (near-zero CPU) waiting for the
            # next input instead of busy-polling at the full framerate.
            target_fps = config.IDLE_FRAMERATE if self._idle_ticks >= IDLE_THRESHOLD_TICKS else self.framerate
            timeout_ms = max(1, int(1000 / target_fps))

            events = [pg.event.wait(timeout_ms)]
            events += pg.event.get()
            deltatime = self.clock.tick(target_fps) / 1000

            for event in events:
                if event.type != pg.NOEVENT:
                    self.handle_event(event)

            self.update(deltatime)
            self.render()
            self.check_gpio_input()

            if self.render_processor.dirty_this_frame:
                self._idle_ticks = 0
            else:
                self._idle_ticks += 1

            self._time_since_save += deltatime
            if self._time_since_save >= AUTOSAVE_INTERVAL:
                self._time_since_save = 0.0
                save_save(save_data)

        save_save(save_data)
        try:
            pg.mixer.quit()
        except:
            pass
