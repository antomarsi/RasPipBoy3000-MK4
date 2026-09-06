import esper
import pygame as pg
from game.data.store import theme
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
        self.groups = EntityGroup()
        self.background = pg.surface.Surface(
            self.screen.get_size()).convert()
        self.background.fill(theme.bg_color)

        # ECS scaffold (esper). Coexists with the sprite-based `self.groups`
        # above until every module is ported off it; see the architecture plan.
        esper.add_processor(TweenProcessor(), priority=50)
        esper.add_processor(AnimationProcessor(), priority=40)
        esper.add_processor(AutoScrollProcessor(), priority=35)

        # Local import: game.ui imports core.engine.Entity at module scope, so
        # importing game.ui.state up at the top of this file (which needs
        # game.ui for UI_MARGIN) would be a circular import at parse time.
        # By the time Engine() is actually constructed, all modules are
        # already fully loaded, so this is safe.
        from game.ui.state import UIRenderProcessor
        esper.add_processor(UIRenderProcessor(), priority=30)

        self.render_processor = RenderProcessor(self.screen)

    def handle_event(self, event):
        pass

    def render(self):
        self.groups.clear(self.screen, self.background)
        self.groups.draw(self.screen)
        self.render_processor.process()

        # Deliberately an unconditional flip while the sprite-based `self.groups`
        # and the ECS render layer coexist: the ECS layer fully recomposites on
        # top every frame (see RenderProcessor), so a partial pg.display.update()
        # here could miss regions the old system just redrew underneath it. Once
        # every module is ported to the ECS and `self.groups` is retired, this
        # can go back to skipping the flip on frames with nothing dirty.
        if self.rescale:
            frame = pg.transform.scale(self.screen, self.window.get_size())
            self.window.blit(frame, (0,0))
        pg.display.flip()

    def update(self, deltatime):
        self.groups.update(deltatime)
        esper.process(deltatime)

    def add(self, group, *args, **kwargs):
        if not self.groups.has(group):
            self.groups.add(group, *args, **kwargs)

    def remove(self, group):
        if self.groups.has(group):
            self.groups.remove(group)


class EntityGroup(pg.sprite.LayeredDirty):

    def update(self, *args, **kwargs):
        for sprite in self.sprites():
            if sprite.active:
                sprite.update(*args, **kwargs)

    def move(self, x, y):
        for child in self:
            child.rect.move(x, y)


class Entity(pg.sprite.DirtySprite):
    active = True

    def __init__(self, dimensions=(0, 0), layer=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pg.surface.Surface(dimensions)
        self.rect = self.image.get_rect()
        self.image = self.image.convert()
        self.layer = layer
        self.dirty = 2
        self.blendmode = pg.BLEND_RGBA_ADD


    def __le__(self, other):
        if type(self) == type(other):
            return self.label <= other.label
        return 0
