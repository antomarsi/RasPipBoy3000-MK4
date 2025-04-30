from core.engine import EntityGroup
from game.ui import SubMenu
from utils.logger import logger
import pygame as pg


class BaseModule(EntityGroup):
    submodules = []
    _active_submodule = None
    active = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance

    def __init__(self, pipboy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipboy = pipboy

        self.action_handlers = {
            "pause": self.handle_pause,
            "resume": self.handle_resume
        }

        self.submenu = SubMenu(self.submodules)
        self.add(self.submenu)


    def switch_submodule(self, module):
        if not len(self.submodules):
            logger.debug(
                f"No Submodule registered on [{self.__class__.__name__}]")
            return
        if module < len(self.submodules) and self._active_submodule != module:
            logger.debug(f"[{self.__class__}] Switching to submodule {module}")
            if self.active:
                self.active.handle_action("pause")
                self.remove(self.active)

            self._active_submodule = module
            self.active = self.submodules[self._active_submodule]
            self.active.parent = self
            self.active.handle_action("resume")
            self.submenu.set_active_index(module)
            self.add(self.active)
        else:
            logger.debug(
                f"No Submodule ({module}) on [{self.__class__.__name__}]")

    def update(self, *args, **kwargs):
        if self.active:
            self.active.update(*args, **kwargs)
        return super().update(*args, **kwargs)

    def handle_action(self, action, value=0):
        if action.startswith("knob_"):
            # if action.startswith("knob_") and not settings.hide_submenu:
            num = int(action[-1])
            self.switch_submodule(num - 1)
        elif action in self.action_handlers:
            self.action_handlers[action]()
        else:
            if self.active:
                self.active.handle_action(action, value)

    def handle_event(self, event):
        if self.active:
            self.active.handle_event(event)

    def handle_pause(self):
        self.paused = True

    def handle_resume(self):
        self.paused = False

    @staticmethod
    def initialize():
        pass


class SubModule(EntityGroup):
    parent = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(*sprites, **kwargs)
        self.parent = parent
        self.paused = True

        self.action_handlers = {
            "pause": self.handle_pause,
            "resume": self.handle_resume
        }

    def handle_action(self, action, value=0):
        if action.startswith("dial_"):
            if hasattr(self, "menu"):
                self.menu.handle_action(action)
        elif action in self.action_handlers:
            self.action_handlers[action]()

    def handle_event(self, event):
        pass

    def handle_pause(self):
        if self.paused == False:
            self.paused = True

    def handle_resume(self):
        if self.paused == True:
            self.paused = False

    @staticmethod
    def initialize():
        pass
