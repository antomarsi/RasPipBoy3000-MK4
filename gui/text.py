import pyglet
from system.component import Component


class Text(Component):

    def __init__(self, text, *args, **kwargs):
        """
        Creates a sprite using a ball image.
        """
        super(Text, self).__init__(*args, **kwargs)
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('y', 0)
        self.text = pyglet.text.Label(
            text,
            font_name=kwargs.get('font_name', 'Times New Roman'),
            font_size=kwargs.get('font_size', 36),
            color=kwargs.get('color', (255, 255, 255, 255)),
            x=self.x, y=self.y,
            anchor_x='left', anchor_y='bottom')
        self.width = kwargs.get('width', self.text.content_width)
        self.height = kwargs.get('height', self.text.content_height)
        self.background = kwargs.get('background', None)

    def get_quads(self):
        return ('v2f', (
            self.x, self.y,
            self.x + self.width, self.y,
            self.x + self.width, self.y + self.height,
            self.x, self.y + self.height))

    def get_colors(self):
        return ('c4B', (
            self.background[0], self.background[1], self.background[2], self.background[3],
            self.background[0], self.background[1], self.background[2], self.background[3],
            self.background[0], self.background[1], self.background[2], self.background[3],
            self.background[0], self.background[1], self.background[2], self.background[3]))

    def update_self(self, dt):
        return

    def on_key_press(self, symbol, modifiers):
        pass

    def draw_self(self):
        """
        Draws our ball sprite to screen
        :return:
        """
        if (self.background is not None):
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self.get_quads(), self.get_colors())

        self.text.draw()
