from xmlrpc.client import Boolean
import pygame as pg
import pygame
from utils.config import config
import time

class Engine(object):

    EVENTS_UPDATE = pygame.USEREVENT + 1
    EVENTS_RENDER = pygame.USEREVENT + 2

    def __init__(self, title, width, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = pygame.display.set_mode((width, height))
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption(title)
        pygame.mouse.set_visible(True)

        self.groups = []
        self.root_children = EntityGroup()
        self.background = pygame.surface.Surface(
            self.screen.get_size()).convert()
        self.background.fill(config.BG_COLOR)

        self.rescale = False

    def render(self, deltatime):
        self.root_children.clear(self.screen, self.background)
        self.root_children.render(deltatime)
        self.root_children.draw(self.screen)
        for group in self.groups:
            group.render(deltatime)
            group.draw(self.screen)
        pygame.display.flip()

    def update(self):
        self.root_children.update()
        for group in self.groups:
            group.update()

    def add(self, group):
        if group not in self.groups:
            self.groups.append(group)

    def remove(self, group):
        if group in self.groups:
            self.groups.remove(group)


class EntityGroup(pygame.sprite.LayeredDirty):
    def render(self, deltatime):
        for entity in self:
            entity.render(deltatime)

    def move(self, x, y):
        for child in self:
            child.rect.move(x, y)


class Entity(pygame.sprite.DirtySprite):
    def __init__(self, dimensions=(0, 0), layer=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.surface.Surface(dimensions)
        self.rect = self.image.get_rect()
        self.image = self.image.convert()
        self.groups = pygame.sprite.LayeredDirty()
        self.layer = layer
        self.dirty = 2
        self.blendmode = pygame.BLEND_RGBA_ADD

    def render(self, deltatime=0, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


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
