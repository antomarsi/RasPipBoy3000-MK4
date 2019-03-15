import pyglet
from system.component import Component


class Text(Component):

    def __init__(self, text, *args, **kwargs):
        """
        Creates a sprite using a ball image.
        """
        super(Text, self).__init__(*args, **kwargs)
        self.text = text
        self.x = kwargs.get('x', 0)
        self.y = kwargs.get('x', 0)
        self.width = kwargs.get('width', 0)
        self.height = kwargs.get('height', 0)

        self.background = kwargs.get('background', None)

        print('Cursor Created')

    def get_quads(self):
        ('v2f', (self.x, self.y,
                 self.x + self.width, self.y,
                 self.x + self.width, self.y + self.height,
                 self.x, self.y + self.height))

    def update_self(self):
        return

    def draw_self(self):
        """
        Draws our ball sprite to screen
        :return:
        """
        if (self.background is not None):
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self.get_quads())

        self.ball_sprite.draw()
