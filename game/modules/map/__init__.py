
from game.modules import BaseModule


class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
        ]
        super().__init__(pipboy, *sprites, **kwargs)

    def __str__(self):
        return "MAP"
