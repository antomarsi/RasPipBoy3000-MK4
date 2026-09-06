import esper
import pygame as pg
from game.data.store import theme
from game.ui import UIRenderProcessor
from core.processors import AnimationProcessor, AutoScrollProcessor, RenderProcessor, TweenProcessor


class Engine():

    EVENTS_UPDATE = pg.USEREVENT + 1
    EVENTS_RENDER = pg.USEREVENT + 2
    rescale = False

    def __init__(self, title, size, output_size = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pg.init()

        if output_size:
            self.window = pg.display.set_mode(output_size)
            self.screen = pg.Surface(size)
            self.rescale = True
        else:
            self.window = pg.display.set_mode(size)
            self.screen = pg.display.get_surface()

        pg.display.set_caption(title)
        pg.mouse.set_visible(False)

        esper.add_processor(TweenProcessor(), priority=50)
        esper.add_processor(AnimationProcessor(), priority=40)
        esper.add_processor(AutoScrollProcessor(), priority=35)
        esper.add_processor(UIRenderProcessor(), priority=30)

        self.render_processor = RenderProcessor(self.screen, theme.bg_color)

    def handle_event(self, event):
        pass

    def render(self):
        self.render_processor.process()

        # Only touch the display when something actually changed this frame --
        # the whole point of dirty_this_frame (battery: skips a scale+blit+flip
        # on an otherwise-static screen).
        if self.render_processor.dirty_this_frame:
            if self.rescale:
                frame = pg.transform.scale(self.screen, self.window.get_size())
                self.window.blit(frame, (0, 0))
            pg.display.flip()

    def update(self, deltatime):
        esper.process(deltatime)
