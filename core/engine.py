import pygame as pg
from utils.config import config

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
        self.background.fill(config.BG_COLOR)

    def handle_event(self, event):
        pass

    def render(self):
        self.groups.clear(self.screen, self.background)
        self.groups.draw(self.screen)

        if self.rescale:
            frame = pg.transform.scale(self.screen, self.window.get_size())
            self.window.blit(frame, (0,0))
        pg.display.flip()

    def update(self, deltatime):
        self.groups.update(deltatime)

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


class AnimatedSprite(pg.sprite.DirtySprite):
    def __init__(self, autoplay=False, loop=False, duration_per_frame=0.2, start_frame=0, images=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autoplay = autoplay
        self.loop = loop
        self.is_playing = self.autoplay
        self.duration_per_frame = duration_per_frame
        self.internal_cd = 0
        self.current_frame = start_frame
        self.finished = False
        self.images = images
        if len(self.images):
            self.image = self.images[0]
            self.rect = self.image.get_rect()

    def set_images(self, images):
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def play(self):
        self.is_playing = True

    def update(self, dt):
        new_frame = self.current_frame
        if self.is_playing:
            if self.internal_cd >= self.duration_per_frame:
                self.internal_cd = 0
                if self.current_frame == len(self.images)-1:
                    if not self.loop:
                        self.is_playing = False
                        self.finished = True
                    else:
                        self.current_frame = 0
                elif self.current_frame < len(self.images)-1:
                    self.current_frame += 1

                self.image = self.images[self.current_frame]
            self.internal_cd += dt
        if new_frame is not self.current_frame:
            self.dirty = 1
