
from game.modules import BaseModule
from game.ui import Footer, Header
from utils.settings import config


class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
        ]
        super().__init__(pipboy, *sprites, **kwargs)
        self.header = Header(label=str(self), options=config.MODULE_TEXTS)
        self.footer = Footer([])
        self.add(self.footer)
        self.add(self.header)
        self.switch_submodule(0)

    def __str__(self):
        return "INV"
