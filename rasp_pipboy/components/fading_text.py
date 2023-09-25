import pygame as pg

class FadingText(pg.sprite.DirtySprite):
    def __init__(self, text:str, font: pg.font.Font, color = (255, 255, 255)):
        pg.sprite.DirtySprite.__init__(self)
        self.image = font.render(text, True, color)
        self.opacity = 255
        self.rect = self.image.get_rect()
        self.fade = True

    def update(self, dt):
        print(f"fading {self.opacity}")
        if self.fade:
            self.opacity -= 100 * dt
            self.opacity = max(self.opacity, 0)
            if (self.opacity == 0):
                self.fade = False
        if not self.fade:
            self.opacity += 100 * dt
            self.opacity = min(self.opacity, 255)
            if (self.opacity == 255):
                self.fade = True
        self.image.set_alpha(self.opacity)
        self.dirty = 1