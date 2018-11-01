import abc, pygame
from gui.GuiElement import GuiElement
from pygame.math import Vector2

class GuiSprite(GuiElement):
    def __init__(self, image, position = (0, 0), scale = None):
        super(GuiSprite, self).__init__()
        self.image = pygame.image.load(image)
        self.set_size(self.image.get_size())
        self.set_relative_position(position)
        if scale is not None:
            self.image = pygame.transform.scale(self.image, scale)

    def draw(self, surface):
        surface.blit(self.image, self.get_absolute_position())

    def update(self, delta_time):
        pass
