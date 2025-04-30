from core.engine import Entity
from game.modules import SubModule


class AidSubModule(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)


    def __str__(self):
        return "AID"
