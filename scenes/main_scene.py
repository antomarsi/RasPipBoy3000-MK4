import pyglet
from gui.text import Text
from scenes.stats import StatsScene
from scenes.maps import MapScene
from scenes.radio import RadioScene
from system.component import Component
import config


class MainScene(Component):

    def __init__(self, *args, **kwargs):
        super(MainScene, self).__init__(*args, **kwargs)
        self.width = config.window_width
        self.height = config.window_height
        self.selectedScene = 4
        self.debugImage()
        self.addScenes()
        self.addMenuLabels()

    def addScenes(self):
        self.scenes = []
        pos = (config.window_width * 0.12, config.window_height * 0.025)
        size = (config.window_width * 0.762, config.window_height*0.875)
        self.scenes.append(StatsScene(x=pos[0],y=pos[1],width=size[0],height=size[1]))
        self.scenes.append(StatsScene(x=pos[0],y=pos[1],width=size[0],height=size[1]))
        self.scenes.append(StatsScene(x=pos[0],y=pos[1],width=size[0],height=size[1]))
        self.scenes.append(MapScene(x=pos[0],y=pos[1],width=size[0],height=size[1]))
        self.scenes.append(RadioScene(x=pos[0],y=pos[1],width=size[0],height=size[1]))

    def addMenuLabels(self):
        sizes = [(config.window_width * 0.223, config.window_height * 0.92),
               (config.window_width * 0.34, config.window_height * 0.92),
               (config.window_width * 0.445, config.window_height * 0.92),
               (config.window_width * 0.572, config.window_height * 0.92),
               (config.window_width * 0.675, config.window_height * 0.92)]
        for idx, scene in enumerate(self.scenes):
            self.addText(scene.title, 'MonoFont', sizes[idx][0],sizes[idx][1], 13);

    def drawSelectionLines(self):
        color = ('c4B', (0, 255, 255, 255, 0, 255, 255, 255))
        selectedTab = self.children[self.selectedScene]
        points = [
            (config.window_width * 0.118, config.window_height * 0.9, config.window_width * 0.118, config.window_height * 0.91),
            (config.window_width * 0.118, config.window_height * 0.91, self.children[self.selectedScene].x-5, config.window_height * 0.91),
            (selectedTab.x-5, config.window_height * 0.91, selectedTab.x-5, config.window_height * 0.91 + selectedTab.height*0.58),
            (selectedTab.x-5, config.window_height * 0.91 + selectedTab.height*0.58, selectedTab.x + selectedTab.width + 5, config.window_height * 0.91 + selectedTab.height*0.58),
            (selectedTab.x + selectedTab.width + 5, config.window_height * 0.91 + selectedTab.height*0.58, selectedTab.x + selectedTab.width + 5, config.window_height * 0.91),
            (selectedTab.x + selectedTab.width + 5, config.window_height * 0.91, config.window_width * 0.883, config.window_height * 0.91),
            (config.window_width * 0.883, config.window_height * 0.91, config.window_width * 0.883, config.window_height * 0.9)

            ]
        for point in points:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2f', point), color)

    def addText(self, text, font='Monofonto', x=200, y=200, font_size=18):
        self.children.append(Text(text, font_name="Monofonto", font_size=font_size, x=x, y=y, color=(
            0, 255, 0, 255), background=(0, 0, 0, 255)))

    def debugImage(self):
        bg_image = pyglet.image.load('assets/temp/menu1.png')
        self.image = pyglet.sprite.Sprite(img=bg_image, x=-50, y=-3)
        self.image.scale = 0.45

    def on_key_press(self, symbol, modifiers):
        pass

    def update_self(self, dt):
        self.scenes[self.selectedScene].update_self(dt)
        for child in self.children:
            if isinstance(child, Component):
                child.update_self(dt)
        return

    def draw_self(self):
        print('teste')
        self.image.draw()
        self.scenes[self.selectedScene].draw_self()
        self.drawSelectionLines()
        for child in self.children:
            if isinstance(child, Component):
                child.draw_self()
        return
