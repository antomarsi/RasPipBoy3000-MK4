import pygame as pg
from rasp_pipboy.utils.config import ConfigSettings


class ScanLineGradient(pg.sprite.DirtySprite):
    def __init__(self):
        pg.sprite.DirtySprite.__init__(self)
        cfg = ConfigSettings()
        self.image = pg.Surface((cfg.width, cfg.height*4), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.image.fill((80, 80, 80, 255))

        self.fill_gradient(self.image, (255, 255, 255, 255), (80, 80, 80, 255), forward=False,
                           rect=pg.Rect(0, self.rect.height/2 - self.rect.height/32, self.rect.width, self.rect.height/16))
        self.fill_gradient(self.image, (255, 255, 255, 255), (80, 80, 80, 255), forward=True,
                           rect=pg.Rect(0, self.rect.height/2 + self.rect.height/32, self.rect.width, self.rect.height/16))

        self.image = self.image.convert_alpha()
        self.start_pos = (-cfg.height*3)
        self.end_pos = -cfg.height*0.75
        self.rect.y = self.start_pos
        self.blendmode = pg.BLEND_RGBA_MULT

    def update(self, dt):
        self.rect.y += 80 * dt
        if (self.rect.y >= self.end_pos):
            self.rect.y = self.start_pos
        self.dirty = 1

    def fill_gradient(self, surface, color, gradient, rect=None, vertical=True, forward=True):
        """fill a surface with a gradient pattern
        Parameters:
        color -> starting color
        gradient -> final color
        rect -> area to fill; default is surface's rect
        vertical -> True=vertical; False=horizontal
        forward -> True=forward; False=reverse
        Pygame recipe: http://www.pg.org/wiki/GradientCode
        """
        if rect is None:
            rect = surface.get_rect()
        x1, x2 = rect.left, rect.right
        y1, y2 = rect.top, rect.bottom
        if vertical:
            h = y2-y1
        else:
            h = x2-x1
        if forward:
            a, b = color, gradient
        else:
            b, a = color, gradient
        rate = (
            float(b[0]-a[0])/h,
            float(b[1]-a[1])/h,
            float(b[2]-a[2])/h,
            float(b[3]-a[3])/h,
        )
        fn_line = pg.draw.line
        if vertical:
            for line in range(y1, y2):
                color = (
                    min(max(a[0]+(rate[0]*(line-y1)), 0), 255),
                    min(max(a[1]+(rate[1]*(line-y1)), 0), 255),
                    min(max(a[2]+(rate[2]*(line-y1)), 0), 255),
                    min(max(a[3]+(rate[3]*(line-y1)), 0), 255),
                )
                vertical_line = pg.Surface((x2, 1), pg.SRCALPHA)
                vertical_line.fill(color)
                surface.blit(vertical_line, (x1, line))
        else:
            for col in range(x1, x2):
                color = (
                    min(max(a[0]+(rate[0]*(col-x1)), 0), 255),
                    min(max(a[1]+(rate[1]*(col-x1)), 0), 255),
                    min(max(a[2]+(rate[2]*(col-x1)), 0), 255),
                    min(max(a[3]+(rate[3]*(col-x1)), 0), 255),
                )
                fn_line(surface, color, (col, y1), (col, y2))
