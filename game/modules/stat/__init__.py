
from game.modules import BaseModule
from game.modules.stat import perks, special, status
from game.ui import Header
from utils.settings import config


class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
            status.Module(self),
            special.Module(self),
            perks.Module(self)
        ]
        super().__init__(pipboy, *sprites, **kwargs)
        self.header = Header(label=str(self), options=config.MODULE_TEXTS)
        self.add(self.header)

    def handle_resume(self):
        self.switch_submodule(0)
        return super().handle_resume()

    def __str__(self):
        return 'STAT'
