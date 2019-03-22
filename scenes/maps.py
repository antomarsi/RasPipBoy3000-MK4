import pyglet
from gui.text import Text
from system.component import Component
import config

class MapScene(Component):

    def __init__(self, *args, **kwargs):
        super(MapScene, self).__init__(*args, **kwargs)
        self.title = "MAPS"
        self.width = kwargs.get('width', config.window_width)
        self.height = kwargs.get('height', config.window_height)
        print('Scene Map Created')

    def drawBG(self):
        background = (255, 0, 255, 255)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
            ('v2f', (
                self.x, self.y,
                self.x + self.width, self.y,
                self.x + self.width, self.y + self.height,
                self.x, self.y + self.height)),
            ('c4B', (
                background[0], background[1], background[2], background[3],
                background[0], background[1], background[2], background[3],
                background[0], background[1], background[2], background[3],
                background[0], background[1], background[2], background[3])))

    def update_self(self, dt):
        for child in self.children:
            if isinstance(child, Component):
                child.update_self(dt)
        return

    def draw_self(self):
        self.drawBG()
        for child in self.children:
            if isinstance(child, Component):
                child.draw_self()
        return
