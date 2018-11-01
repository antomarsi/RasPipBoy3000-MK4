import abc, pygame
from gui.GuiElement import GuiElement
from pygame.math import Vector2

class GuiFillBar(GuiElement):
    def __init__(self, color = None, rect = (0,0, 100, 10), line_width = 2, max_value = 10, value = 0):
        super(GuiFillBar, self).__init__()
        self.color = color
        self.set_size((rect[2], rect[3]))
        self.line_width = 2
        self.set_relative_position((rect[0], rect[1]))
        self.max_value = max_value
        self.set_value(value)

    def compute_fill_rect(self):
        width = self.rect.width
        width = width * (self.value / self.max_value)
        self.fill_rect = pygame.Rect((self.rect.x, self.rect.y, width, self.rect.height))

    def set_value(self, value):
        self.value = max(min(value, self.max_value), 0)
        self.compute_fill_rect()

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, self.line_width)
        pygame.draw.rect(surface, self.color, self.fill_rect)

    def update(self, delta_time):
        pass
