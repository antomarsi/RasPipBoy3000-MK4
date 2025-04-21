
from game.modules import BaseModule
from game.modules.stats.status import StatusSubModule


class StatsModule(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
            StatusSubModule(self)
        ]
        super().__init__(pipboy, *sprites, **kwargs)


    def __str__(self):
        return "STAT"
