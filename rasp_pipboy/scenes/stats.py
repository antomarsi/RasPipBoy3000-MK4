from .scene_base import SceneBase
import pygame as pg
from pygame.locals import *
import rasp_pipboy.utils.config as cfg
from rasp_pipboy.components.animated_sprite import AnimatedSprite
from rasp_pipboy.components.header import Header
from rasp_pipboy.components.sub_header import SubHeader
import os
import json
import time
import threading
import rasp_pipboy.graphics.fonts as fonts
from rasp_pipboy.core.resource_loader import ResourceLoader
from rasp_pipboy.components.sound_click import SoundClick


class DebugImage(pg.sprite.DirtySprite):
    def __init__(self):
        super().__init__()

        self.image = ResourceLoader.getInstance().get_image('temp/menu1.png')
        self.image = pg.transform.smoothscale(self.image, (int(
            self.image.get_width()*0.45), int(self.image.get_height()*0.45))).convert()
        self.rect = self.image.get_rect()
        self.dirty = 1

    def set_opacity(self, value):
        self.image.set_alpha(value)
        self.dirty = 1


class BottomBar(pg.sprite.DirtySprite):
    def __init__(self, rect, color=(255, 255, 255)):
        super().__init__()
        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.rect = rect
        self.color = color
        self.background = (color[0], color[1], color[2], 255/4)
        self.hp = [155, 155]
        self.ap = [90, 90]
        self.level = 1
        self.xp = [35, 100]
        self.font = fonts.MONOFONTO_14
        self.font.set_bold(True)
        self.draw_hp()
        self.draw_ap()
        self.draw_xp()
        self.dirty = 1

    def draw_hp(self):
        pg.draw.rect(self.image, self.background,
                     (2, 0, self.rect.width*0.24, self.rect.height))
        text_sur = self.font.render("HP %d/%d" %
                                    (self.hp[0], self.hp[1]), True, self.color)
        self.image.blit(text_sur, (5, 0))

    def draw_ap(self):
        pos_rect = pg.Rect(self.rect.width*0.77, 0,
                           self.rect.width*0.23, self.rect.height)
        pg.draw.rect(self.image, self.background, pos_rect)
        text_sur = self.font.render("AP %d/%d" %
                                    (self.ap[0], self.ap[1]), True, self.color)
        self.image.blit(
            text_sur, (pos_rect.x + pos_rect.width - text_sur.get_width(), 0))

    def draw_xp(self):
        pos_rect = pg.Rect(self.rect.width*0.25, 0,
                           self.rect.width*0.515, self.rect.height)
        pg.draw.rect(self.image, self.background, pos_rect)
        text_sur = self.font.render("LEVEL %d" % self.level, True, self.color)
        self.image.blit(text_sur, (pos_rect.x+3, 0))
        bar_rect = pg.Rect(pos_rect.x + text_sur.get_width()+8, self.rect.height/4,
                           pos_rect.width - text_sur.get_width() - 16, self.rect.height/2)
        pg.draw.rect(self.image, self.color, bar_rect, 2)
        bar_rect.width = bar_rect.width * (self.xp[0]/self.xp[1])
        pg.draw.rect(self.image, self.color, bar_rect)


class StatusMenu(pg.sprite.DirtySprite):
    def __init__(self, rect, color=(255, 255, 255)):
        super().__init__()
        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.rect = rect
        self.color = color
        self.background = (color[0], color[1], color[2], 255/2)
        self.dark_color = (color[0]/4, color[1]/4, color[2]/4, 255/8)
        self.font = fonts.MONOFONTO_12
        self.stimpaks = 0
        self.radaway = 0
        self.font.set_bold(True)
        self.draw_buttons()
        self.health_parts = {
            "head": 1,
            "larm": 1,
            "rarm": 1,
            "lleg": 1,
            "rleg": 1,
            "health": 1
        }
        self.low_bar = {
            "aim": 79,
            "shield": 10,
            "lightning": 20,
            "radiation": 10
        }
        self.draw_low_bar_stats()
        self.draw_health_parts()
        self.dirty = 1

    def draw_low_bar_stats(self):
        # Weapon
        rect = pg.Rect(self.rect.width*0.284, self.rect.height *
                       0.745, self.rect.width*0.090, self.rect.height*0.125)
        pg.draw.rect(self.image, self.background, rect)

        # Aim
        rect = pg.Rect(self.rect.width*0.384, self.rect.height *
                       0.745, self.rect.width*0.05, self.rect.height*0.125)
        pg.draw.rect(self.image, self.background, rect)

        text_sur = self.font.render(
            str(self.low_bar["aim"]), True, self.color).convert_alpha()

        self.image.blit(
            text_sur, (rect.centerx - text_sur.get_width()/2 + self.rect.width*0.004, rect.centery))

        # Armor
        rect = pg.Rect(self.rect.width*0.464, self.rect.height *
                       0.745, self.rect.width*0.092, self.rect.height*0.125)
        pg.draw.rect(self.image, self.background, rect)

        # Shield
        rect = pg.Rect(self.rect.width*0.564, self.rect.height *
                       0.745, self.rect.width*0.05, self.rect.height*0.125)
        pg.draw.rect(self.image, self.background, rect)

        text_sur = self.font.render(
            str(self.low_bar["shield"]), True, self.color).convert_alpha()

        self.image.blit(
            text_sur, (rect.centerx - text_sur.get_width()/2 + self.rect.width*0.004, rect.centery))

        # Lightning
        rect = pg.Rect(self.rect.width*0.624, self.rect.height *
                       0.745, self.rect.width*0.05, self.rect.height*0.125)
        pg.draw.rect(self.image, self.background, rect)

        text_sur = self.font.render(
            str(self.low_bar["lightning"]), True, self.color).convert_alpha()

        self.image.blit(
            text_sur, (rect.centerx - text_sur.get_width()/2 + self.rect.width*0.004, rect.centery))

        # Radiation
        rect = pg.Rect(self.rect.width*0.684, self.rect.height *
                       0.745, self.rect.width*0.05, self.rect.height*0.125)
        pg.draw.rect(self.image, self.background, rect)

        text_sur = self.font.render(
            str(self.low_bar["radiation"]), True, self.color).convert_alpha()

        self.image.blit(
            text_sur, (rect.centerx - text_sur.get_width()/2 + self.rect.width*0.004, rect.centery))

        pass

    def draw_buttons(self):
        text_sur = self.font.render("STIMPAK(%d)" % (
            self.stimpaks), True, self.dark_color).convert_alpha()
        text_sur.set_alpha(0.1)
        start_pos = pg.Rect(2, self.rect.height - text_sur.get_height() - 8,
                            text_sur.get_width() + 4, text_sur.get_height() + 4)
        pg.draw.rect(self.image, self.background, start_pos)
        self.image.blit(
            text_sur, (start_pos.x + 2, start_pos.y+2))

        text_sur = self.font.render("RADAWAY(%d)" % (
            self.radaway), True, self.dark_color).convert_alpha()
        start_pos = pg.Rect(start_pos.x + start_pos.width + 5, self.rect.height - text_sur.get_height() - 8,
                            text_sur.get_width() + 4, text_sur.get_height() + 4)
        pg.draw.rect(self.image, self.background, start_pos)
        self.image.blit(
            text_sur, (start_pos.x + 2, start_pos.y+2))

    def draw_health_parts(self):
        self.draw_progress_bar(pg.Rect(
            self.rect.width*0.512, self.rect.height*0.135, self.rect.width*0.06, self.rect.height*0.024), self.color, self.health_parts.get("head"), True)
        self.draw_progress_bar(pg.Rect(
            self.rect.width*0.325, self.rect.height*0.338, self.rect.width*0.06, self.rect.height*0.024), self.color, self.health_parts.get("rarm"), True)
        self.draw_progress_bar(pg.Rect(
            self.rect.width*0.68, self.rect.height*0.338, self.rect.width*0.06, self.rect.height*0.024), self.color, self.health_parts.get("larm"), True)
        self.draw_progress_bar(pg.Rect(
            self.rect.width*0.325, self.rect.height*0.59, self.rect.width*0.06, self.rect.height*0.024), self.color, self.health_parts.get("rleg"), True)
        self.draw_progress_bar(pg.Rect(
            self.rect.width*0.68, self.rect.height*0.59, self.rect.width*0.06, self.rect.height*0.024), self.color, self.health_parts.get("lleg"), True)
        self.draw_progress_bar(pg.Rect(
            self.rect.width*0.512, self.rect.height*0.695, self.rect.width*0.06, self.rect.height*0.024), self.color, self.health_parts.get("health"), True)

    def draw_progress_bar(self, rect, color, percentage=1, center=False):
        if center:
            rect.x = rect.x - (rect.width/2)
            rect.y = rect.y - (rect.height/2)
        pg.draw.rect(self.image, color, rect, 1)
        rect.width = rect.width * percentage
        pg.draw.rect(self.image, color, rect)


class StatsScene(SceneBase):

    def __init__(self):
        super().__init__()
        screen_size = int(cfg.width * 0.75), int(cfg.height)
        self.surface = pg.Surface(screen_size).convert_alpha()

        background = pg.Surface(self.surface.get_size())
        background.fill((10, 0, 0))
        self.sprites = pg.sprite.LayeredDirty()

        self.debug_image = DebugImage()
        self.debug_image.rect.center = self.surface.get_rect().center
        self.sprites.add(self.debug_image)
        self.header = Header(rect=pg.Rect(
            0, 0, self.surface.get_width(), cfg.height*0.11), selected_index=0)
        self.sprites.add(self.header)
        self.sub_menu = SubHeader(self.header.get_selected_index_position(
        ), self.header.rect.height-5, texts=['STATUS', 'SPECIAL', 'PERKS'])
        self.sprites.add(self.sub_menu)
        self.sprites.add(StatusMenu(pg.Rect(
            0, cfg.height*0.11, self.surface.get_width(), self.surface.get_height()-(cfg.height*0.11)-28)))
        self.sprites.add(BottomBar(rect=pg.Rect(
            0, self.surface.get_height()-28, self.surface.get_width(), 18)))

        self.sprites.clear(self.surface, background)
        pg.time.delay(800)

    def move_sub_menu(self, next=True):
        current_index = self.sub_menu.selected_index
        if next == True:
            self.sub_menu.next_index()
        else:
            self.sub_menu.prev_index()

        is_same_index = current_index == self.sub_menu.selected_index
        if not is_same_index:
            SoundClick.play_horizontal()
        self.sub_menu.rect.x = self.header.get_selected_index_position() - \
            self.sub_menu.get_index_pos()

    def process_input(self, events, keys):
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_F4:
                    self.debug_image.visible = not self.debug_image.visible
                elif event.key == K_d:
                    self.move_sub_menu()
                elif event.key == K_a:
                    self.move_sub_menu(False)

    def update(self, dt):
        self.sprites.update(dt)
        pass

    def render(self, render):
        self.sprites.draw(self.surface)
        render.blit(self.surface, (render.get_width() * 0.125, 0))
        pass
