from core.engine import Entity
from game.modules import SubModule


class Module(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)

    def handle_resume(self):
        return super().handle_resume()
