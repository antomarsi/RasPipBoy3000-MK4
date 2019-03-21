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
        self.selectedScene = 0
        self.debugImage()

        self.addText('STAT', 'MonoFont', config.window_width * 0.275, config.window_height * 0.91, 14);
        self.addText('INV', 'MonoFont', config.window_width * 0.375, config.window_height * 0.91, 14);
        self.addText('DATA', 'MonoFont', config.window_width * 0.46, config.window_height * 0.91, 14);
        self.addText('MAP', 'MonoFont', config.window_width * 0.564, config.window_height * 0.91, 14);
        self.addText('RADIO', 'MonoFont', config.window_width * 0.65, config.window_height * 0.91, 14);

    def drawSelectionLines(self):
        color = ('c4B', (0, 255, 0, 255, 0, 255, 0, 255))
        selectedTab = self.children[self.selectedScene]
        points = [
            (config.window_width * 0.185, config.window_height * 0.9, config.window_width * 0.185, config.window_height * 0.91),
            (config.window_width * 0.185, config.window_height * 0.91, self.children[self.selectedScene].x-5, config.window_height * 0.91),
            (selectedTab.x-5, config.window_height * 0.91, selectedTab.x-5, config.window_height * 0.91 + selectedTab.height*0.58),
            (selectedTab.x-5, config.window_height * 0.91 + selectedTab.height*0.58, selectedTab.x + selectedTab.width + 5, config.window_height * 0.91 + selectedTab.height*0.58),
            (selectedTab.x + selectedTab.width + 5, config.window_height * 0.91 + selectedTab.height*0.58, selectedTab.x + selectedTab.width + 5, config.window_height * 0.91),
            (selectedTab.x + selectedTab.width + 5, config.window_height * 0.91, config.window_width * 0.822, config.window_height * 0.91),
            (config.window_width * 0.822, config.window_height * 0.91, config.window_width * 0.822, config.window_height * 0.9)

            ]
        for point in points:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', point), color)

    def addText(self, text, font='Monofonto', x=200, y=200, font_size=18):
        self.children.append(Text(text, font_name="Monofonto", font_size=font_size, x=x, y=y, color=(
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
        self.drawSelectionLines()
        for child in self.children:
            if isinstance(child, Component):
                child.draw_self()
        return
