from .scene_base import SceneBase
import pygame as pg
import config as cfg
from components.animated_sprite import AnimatedSprite
from components.header import Header
import os, json, time, threading, fonts
from resource import Resource

class DebugImage(pg.sprite.DirtySprite):
    def __init__(self):
        super().__init__()

        self.image = Resource.getInstance().get_image('temp/menu1.png')
        self.image = pg.transform.smoothscale(self.image, (int(self.image.get_width()*0.45), int(self.image.get_height()*0.45))).convert()
        self.rect = self.image.get_rect()
        self.dirty = 2

    def set_opacity(self, value):
        self.image.set_alpha(value)

class StatsScene(SceneBase):

    def __init__(self):
        super().__init__()
        screen_size = int(cfg.width), int(cfg.height)
        self.surface = pg.Surface(screen_size).convert_alpha()

        background = pg.Surface(self.surface.get_size())
        background.fill((0,0,0))
        self.sprites = pg.sprite.LayeredDirty()

        debug_image = DebugImage()
        debug_image.rect.center = self.surface.get_rect().center
        self.sprites.add(debug_image)


        self.sprites.add(Header(pg.Rect(0,0, cfg.width, cfg.height*0.11)))
        self.sprites.clear(self.surface, background)
        pg.time.delay(800)

    def process_input(self, events, keys):
        pass

    def update(self, dt):
        self.sprites.update(dt)
        pass

    def render(self, render):
        self.sprites.draw(self.surface)
        render.blit(self.surface, (0,0))
        pass
