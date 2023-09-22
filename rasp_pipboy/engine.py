import pygame as pg
from pygame.locals import *
from rasp_pipboy.utils.config import ConfigSettings
from rasp_pipboy.utils.shaders import Shader
from rasp_pipboy.scenes.main_scene import MainScene
from scanline_gradient import ScanLineGradient
from rasp_pipboy.core.resource_loader import ResourceLoader

class Engine():

    def __init__(self, fps_limit):
        self.screen = pg.Surface(pg.display.get_surface().get_size()).convert(
            (16711680, 65280, 255, 0), 0)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps_limit = fps_limit
        self.running = True

        for size in [12, 14, 16, 18]:
            ResourceLoader.getInstance().add_font("MONOFONTO", "monofonto.ttf", size)

        self.main_scene = MainScene()

        self.shader = Shader(self.screen)
        self.font = pg.font.Font(None, 30)
        self.show_fps = False
        self.sprite_list = pg.sprite.LayeredDirty((ScanLineGradient()))

    def event_loop(self):
        pressed_keys = pg.key.get_pressed()
        filtered_events = []
        for event in pg.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_F3:
                    self.show_fps = not self.show_fps
                elif event.key == K_ESCAPE:
                    self.running = False
            if self.running == False and self.main_scene != None:
                self.main_scene.terminate()
            else:
                filtered_events.append(event)

        if self.main_scene != None:
            self.main_scene.process_input(filtered_events, pressed_keys)

    def update(self, dt: float):
        """
        Update must acccept and pass dt to all elements that need to update.
        """
        if self.main_scene != None:
            self.main_scene.update(dt)
        self.sprite_list.update(dt)

    def render(self):
        """
        Render all needed elements and update the display.
        """
        self.screen.fill(ConfigSettings().bg_color)

        if self.main_scene != None:
            self.main_scene.render(self.screen)
        self.sprite_list.draw(self.screen)

        if self.show_fps:
            self.screen.blit(self.font.render(
                str(int(self.clock.get_fps())), True, pg.Color('white')), (10, 10))

        self.shader.render(self.screen)
        pg.display.flip()

    def main_loop(self):
        """
        We now use the return value of the call to self.clock.tick to
        get the time delta between frames.
        """
        dt = 0
        self.clock.tick(self.fps_limit)
        while self.running:
            self.event_loop()
            self.update(dt)
            self.render()
            ResourceLoader.getInstance().update()

            dt = self.clock.tick(self.fps_limit)/1000.0