from game.modules import SubModule
from game.ui import Footer


class Module(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)

        self.footer = Footer(["HP 90/100", [["LEVEL 120"], 2], "AP 90/90"])
        self.add(self.footer)


    def __str__(self):
        return "STATUS"
