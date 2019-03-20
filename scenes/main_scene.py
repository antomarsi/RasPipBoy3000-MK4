import pyglet
from gui.text import Text
from scenes.stats import StatsScene
from system.component import Component
import config


class MainScene(Component):

    def __init__(self, *args, **kwargs):
        """
        Creates a sprite using a ball image.
        """
        super(MainScene, self).__init__(*args, **kwargs)
        self.width = config.window_width
        self.height = config.window_height
        self.scenes = []
        self.scenes.append(StatsScene())
        self.debugImage()
        for scene in self.scenes:
            self.addText(scene.title)
        self.addText('STATS', 'MonoFont', 100, 200);
        print('Main Scene Created')

    def addText(self, text, font='Monofonto', x=200, y=200):
        self.children.append(Text(text, font_name="Monofonto", font_size=18, x=x, y=y, color=(
            0, 255, 0, 255), background=(0, 0, 0, 255)))

    def debugImage(self):
        bg_image = pyglet.image.load('assets/temp/menu1.png')
        self.image = pyglet.sprite.Sprite(img=bg_image, x=0, y=0)
        self.image.scale = 0.5

    def update_self(self, dt):
        for child in self.children:
            if isinstance(child, Component):
                child.update_self(dt)
        return

    def draw_self(self):
        """
        Draws our ball sprite to screen
        :return:
        """
        self.image.draw()
        for child in self.children:
            if isinstance(child, Component):
                child.draw_self()
        return
