import abc, pygame
from gui.GuiElement import GuiElement
from pygame.math import Vector2
from enum import Enum

class Alignment(Enum):
    CENTER = 1
    LEFT = 2
    RIGHT = 3

class GuiFillLabel(GuiElement):
    def __init__(self, text, font, rect, margin = None, color = (0, 0, 0, 0), bgcolor = None, alignment = Alignment.LEFT):
        super(GuiFillLabel, self).__init__()
        self.font = font
        self.bgcolor = bgcolor
        self.alignment = alignment
        self.margin = margin
        self.color = color
        self.set_text(text)
        self.set_rect(rect)
        self.compute_text_position()

    def set_text(self, text):
        self.text = text
        new_size = self.font.size(text)
        self.set_size(new_size)
        self.compute_text_position()

    def set_rect(self, rect):
        rect = pygame.Rect(rect)
        self.set_relative_position((rect.x, rect.y))
        text_size = self.font.size(self.text)
        if rect.width < text_size[0]:
            rect.width = text_size[0]
        if rect.height < text_size[1]:
            rect.height = text_size[1]
        self.set_size(rect.size)

    def compute_text_position(self):
        self.text_position = self.get_absolute_position()
        if self.alignment == Alignment.CENTER:
            self.text_position = self.get_absolute_position()
        elif self.alignment == Alignment.RIGHT:
            text_size = self.font.size(self.text)
            text_spacing = self.rect.width - text_size[0]
            self.text_position = (self.text_position[0] + text_spacing, self.text_position[1])
            if self.margin is not None:
                self.text_position = (self.text_position[0] - self.margin[0], self.text_position[1] + self.margin[1])
        elif self.margin is not None:
            self.text_position = (self.text_position[0] + self.margin[0], self.text_position[1] + self.margin[1])
        print(self.text_position)


    def draw(self, surface):
        if not self.visible:
            return
        if self.bgcolor is not None:
            pygame.draw.rect(surface, self.bgcolor, self.rect)
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.text_position)

    def update(self, delta_time):
        pass
