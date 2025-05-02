
from game.modules import BaseModule
from game.modules.boot import boot_text, pip_os, thumbs_up
from utils.events import BOOT_EVENT


class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
            boot_text.Module(self),
            pip_os.Module(self),
            thumbs_up.Module(self)
        ]
        super().__init__(pipboy, *sprites, **kwargs)
        self.submenu.visible = False
        self.submenu.active = False


    def handle_event(self, event):
        if event.type == BOOT_EVENT:
            self.switch_submodule(event.scene)
        return super().handle_event(event)

    def handle_resume(self):
        if not self.active:
            self.switch_submodule(0)
        self.active.handle_action("resume")
        return super().handle_resume()

