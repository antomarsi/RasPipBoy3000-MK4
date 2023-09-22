import pygame as pg


class AnimatedSprite(pg.sprite.DirtySprite):
    def __init__(self, autoplay=False, loop=False, duration_per_frame=0.2, start_frame=0, images = []):
        pg.sprite.DirtySprite.__init__(self)
        self.autoplay = autoplay
        self.loop = loop
        self.is_playing = self.autoplay
        self.duration_per_frame = duration_per_frame
        self.images = []
        self.internal_cd = 0
        self.current_frame = start_frame
        self.finished = False
        self.images = images

    def set_images(self, images):
        self.images = images

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
