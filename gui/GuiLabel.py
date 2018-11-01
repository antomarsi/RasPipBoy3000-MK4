import abc, pygame
from gui.GuiElement import GuiElement
from pygame.math import Vector2

class GuiLabel(GuiElement):
    def __init__(self, text, font, color = (0, 0, 0), position = (0, 0), bgcolor = None):
        super(GuiLabel, self).__init__()
        self.font = font
        self.set_text(text)
        self.color = color
        self.set_relative_position(position)
        self.bgcolor = bgcolor


    def set_text(self, text):
        self.text = text
        new_size = self.font.size(text)
        self.set_size(new_size)

    def draw(self, surface):
        if self.bgcolor is not None:
            pygame.draw.rect(surface, self.bgcolor, self.rect)
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.get_absolute_position())

    def update(self, delta_time):
        pass
