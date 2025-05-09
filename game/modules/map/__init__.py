
from datetime import datetime
from core.engine import Entity
from game.modules import BaseModule, SubModule
from game.ui import Footer, Header
from utils.settings import config

class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
            MapSubmodule(self)
        ]
        super().__init__(pipboy, *sprites, **kwargs)
        self.header = Header(label=str(self), options=config.MODULE_TEXTS)
        self.footer = Footer(["10.23.2287","6:02 PM", ("LOCAL MAP", 2)])
        self.add(self.footer)
        self.add(self.header)
        self.switch_submodule(0)

    def handle_resume(self):
        self.switch_submodule(0)
        return super().handle_resume()

    def get_time(self):
        now = datetime.now()
        date = f"{now.strftime('%d')}.{now.strftime('%m')}.{now.strftime('%Y')}"
        time = now.strftime("%H:%M:%S")
        return date, time

    def update(self, *args, **kwargs):
        date, time = self.get_time()
        if self.footer.update_section(0, date) or self.footer.update_section(1, time):
            self.footer.render([0, 1])
        return super().update(*args, **kwargs)

    def __str__(self):
        return "MAP"


class MapSubmodule(SubModule):
    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)


class Map(Entity):
    def __init__(self, dimensions=..., layer=0, *args, **kwargs):
        super().__init__(dimensions, layer, *args, **kwargs)
