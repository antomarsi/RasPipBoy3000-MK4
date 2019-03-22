import pyglet
from gui.text import Text
from system.component import Component
import config

class StatsScene(Component):

    def __init__(self, *args, **kwargs):
        super(StatsScene, self).__init__(*args, **kwargs)
        self.title = "STATS"
        self.width = config.window_width
        self.height = config.window_height
        #self.addText()
        print('Scene Stats Created')

    def addText(self):
        self.children.append(Text("Hello World", font_name="Monofonto", x=200,y=200, color=(0,255,0,255), background=(0,255,0,122)))
    def update_self(self, dt):
        for child in self.children:
            if isinstance(child, Component):
                child.update_self(dt)
        return

    def draw_self(self):
        for child in self.children:
            if isinstance(child, Component):
                child.draw_self()
        return
