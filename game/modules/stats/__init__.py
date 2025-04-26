
from game.modules import BaseModule
from game.modules.stats.perks import PerksSubModule
from game.modules.stats.status import StatusSubModule
from game.modules.stats.special import SpecialSubModule


class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
            StatusSubModule(self),
            SpecialSubModule(self),
            PerksSubModule(self)
        ]
        super().__init__(pipboy, *sprites, **kwargs)

    def __str__(self):
        return "STAT"
