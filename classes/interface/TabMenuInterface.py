from classes.interface.MenuInterface import MenuInterface

class TabMenuInterface(MenuInterface):

    @property
    def name(self):
        raise NotImplementedError
