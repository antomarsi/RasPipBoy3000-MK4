import abc, pygame
from pygame.math import Vector2

class GuiElement(metaclass=abc.ABCMeta):

    def __init__(self):
        self.parent = None
        self.screen = None
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.visible = True

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent
        self.set_relative_position(self.rect)

    def set_relative_position(self, point):
        if (self.parent is not None):
            point[0] += parent.rect.x
            point[1] += parent.rect.y
        self.rect = pygame.Rect(point, self.rect.size)

    def get_relative_position(self):
        if (self.parent is not None):
            return (self.rect.x - self.parent.rect.x, self.rect.y - self.parent.rect.y)
        else:
            return self.get_absolute_position()

    def get_absolute_position(self):
        return (self.rect.x, self.rect.y)

    def set_size(self, point):
        self.rect.size = point

    @abc.abstractmethod
    def update(self, delta_time):
        pass

    @abc.abstractmethod
    def draw(self):
        pass
