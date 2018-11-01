import abc, pygame
from gui.IHasChild import IHasChild
from pygame.math import Vector2

class GuiScreen(IHasChild):
    def __init__(self):
        self.type = None;
        self.childElements = {}

    def add_element(self, id, element):
        self.childElements[id] = element

    def get_element(self, id):
        return self.childElements[id]

    def draw(self, surface):
        for key, value in self.childElements.items():
            value.draw(surface)

    def update(self, delta_time):
        for key, value in self.childElements.items():
            value.update(delta_time)
        pass

    def event(self):
        pass
