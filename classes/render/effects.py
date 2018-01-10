import pygame
from PIL import Image, ImageFilter

class Effects(object):

    @staticmethod
    def blur_surf(surface, radius, opacity = 1):
        size, image_mode, raw = surface.get_size(), 'RGBA', pygame.image.tostring(surface, 'RGBA')
        pil_blured = Image.frombytes('RGBA', size, raw).filter(ImageFilter.GaussianBlur(radius=radius))

        return pygame.image.fromstring(pil_blured.tobytes('raw', 'RGBA'), size, image_mode)
    
    @staticmethod
    def draw_progressbar(img, position, value, max_value):
        percentage = (value/max_value)
        if percentage != 1:
            pygame.draw.rect(img, (255, 255, 255), position, 1)
            position.width *= percentage
        pygame.draw.rect(img, (255, 255, 255), position)

    @staticmethod
    def aspect_scale(img, bx, by):
        ix,iy = img.get_size()
        if ix > iy:
            # fit to width
            scale_factor = bx/float(ix)
            sy = scale_factor * iy
            if sy > by:
                scale_factor = by/float(iy)
                sx = scale_factor * ix
                sy = by
            else:
                sx = bx
        else:
            # fit to height
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            if sx > bx:
                scale_factor = bx/float(ix)
                sx = bx
                sy = scale_factor * iy
            else:
                sy = by
        return pygame.transform.scale(img, (int(sx),int(sy)))
class Unit():
    def __init__(self, cooldown):
        self.last = pygame.time.get_ticks()
        self.cooldown = cooldown

    def fire(self):
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            return True
        return False