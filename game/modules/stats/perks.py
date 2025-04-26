from core.engine import Entity
from game.modules import SubModule


class PerksSubModule(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)


    def __str__(self):
        return "PERKS"
