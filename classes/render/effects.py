import pygame
from PIL import Image, ImageFilter

class Effects(object):

    @staticmethod
    def blur_surf(surface, radius):
        size, image_mode, raw = surface.get_size(), 'RGB', pygame.image.tostring(surface, 'RGB')
        pil_blured = Image.frombytes('RGB', size, raw).filter(ImageFilter.GaussianBlur(radius=radius))

        return pygame.image.fromstring(pil_blured.tobytes('raw', 'RGB'), size, image_mode)

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