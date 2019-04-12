from .scene_base import SceneBase
import pygame as pg
from pygame.locals import *
import config as cfg
from components.animated_sprite import AnimatedSprite
from components.header import Header
from components.sub_header import SubHeader
import os, json, time, threading, fonts
from resource import Resource

class DebugImage(pg.sprite.DirtySprite):
    def __init__(self):
        super().__init__()

        self.image = Resource.getInstance().get_image('temp/menu1.png')
        self.image = pg.transform.smoothscale(self.image, (int(self.image.get_width()*0.45), int(self.image.get_height()*0.45))).convert()
        self.rect = self.image.get_rect()
        self.dirty = 1

    def set_opacity(self, value):
        self.image.set_alpha(value)
        self.dirty = 1

class BottomBar(pg.sprite.DirtySprite):
    def __init__(self, rect, color=(255,255,255)):
        super().__init__()
        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.rect = rect
        self.color = color
        self.hp = [155, 155]
        self.level = 1
        self.xp = [35, 100]
        self.draw_hp()
        self.dirty=1

    def draw_hp(self):
        pg.draw.rect(self.image, self.color, self.rect)

class StatsScene(SceneBase):

    def __init__(self):
        super().__init__()
        screen_size = int(cfg.width * 0.75), int(cfg.height)
        self.surface = pg.Surface(screen_size).convert_alpha()

        background = pg.Surface(self.surface.get_size())
        background.fill((0,0,0))
        self.sprites = pg.sprite.LayeredDirty()

        self.debug_image = DebugImage()
        self.debug_image.rect.center = self.surface.get_rect().center
        self.sprites.add(self.debug_image)
        self.header = Header(rect=pg.Rect(0, 0, self.surface.get_width(), cfg.height*0.11), selected_index=0)
        self.sprites.add(self.header)
        self.sprites.add(BottomBar(pg.Rect(0, self.surface.get_height() - 20,self.surface.get_width(), 20)))
        self.sub_menu = SubHeader(self.header.get_selected_index_position(), self.header.rect.height-5, texts=['STATUS', 'SPECIAL', 'PERKS'])
        self.sprites.add(self.sub_menu)

        self.sprites.clear(self.surface, background)
        pg.time.delay(800)

    def process_input(self, events, keys):
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_F4:
                    self.debug_image.visible = not self.debug_image.visible
                elif event.key == K_d:
                    self.sub_menu.next_index()
                    self.sub_menu.rect.x = self.header.get_selected_index_position() - self.sub_menu.get_index_pos()
                elif event.key == K_a:
                    self.sub_menu.prev_index()
                    self.sub_menu.rect.x = self.header.get_selected_index_position() - self.sub_menu.get_index_pos()

    def update(self, dt):
        self.sprites.update(dt)
        pass

    def render(self, render):
        self.sprites.draw(self.surface)
        render.blit(self.surface, (render.get_width() * 0.125,0))
        pass
