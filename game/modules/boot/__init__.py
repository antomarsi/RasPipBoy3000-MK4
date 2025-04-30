
from game.modules import BaseModule
from game.modules.boot import boot_text, pip_os, thumbs_up


class Module(BaseModule):

    def __init__(self, pipboy, *sprites, **kwargs):
        self.submodules = [
            boot_text.Module(self),
            pip_os.Module(self),
            thumbs_up.Module(self)
        ]
        super().__init__(pipboy, *sprites, **kwargs)
        self.switch_submodule(0)

    def handle_resume(self):
        self.submenu.visible = False
        self.active.handle_action("resume")
