import pygame, config_new as config
from abc import ABCMeta, abstractmethod

class Tab(metaclass=ABCMeta):

    subMenus = []
    selectedSubmenu = 0
    footerSize = (config.WIDTH*0.9, config.MEDcharHeight)
    @property
    @abstractmethod
    def tabName(self):
        pass

    @property
    @abstractmethod
    def subMenus(self):
        pass

    def changeSubMenu(self, subMenuIndex):
        if subMenuIndex < len(self.subMenus):
            self.selectedSubmenu = subMenuIndex
        else:
            print("Tried to select a non-valid SubMenu")

    @abstractmethod
    def draw(self):
        return pygame.Surface(self.footerSize)

    @abstractmethod
    def drawFooter(self, character):
        raise NotImplementedError

class TabStat(Tab):

    tabName = "STAT"
    subMenus = []

    def draw(self):
        pass

    def drawFooter(self, character):
        img = super().draw()
        pygame.draw.rect(img, (80, 80, 0), (0, 0, (img.get_width()/4)-(config.SMLcharWidth/2), img.get_height() ), 0)
        pygame.draw.rect(img, (80, 80, 0), ((img.get_width()/4)+(config.SMLcharWidth/2), 0, ((img.get_width()/4)*2)-(config.SMLcharWidth/2), img.get_height() ), 0)
        pygame.draw.rect(img, (80, 80, 0), (((img.get_width()/4)*2)+(config.SMLcharWidth), 0, img.get_width(), img.get_height() ), 0)
        
        return img

class TabInv(Tab):

    tabName = "INV"
    subMenus = []

    def draw(self):
        pass

    def drawFooter(self, character):
        pass

class TabData(Tab):

    tabName = "DATA"
    subMenus = []

    def draw(self):
        pass
    def drawFooter(self, character):
        pass
class TabMap(Tab):

    tabName = "DATA"
    subMenus = []

    def draw(self):
        pass
    def drawFooter(self, character):
        pass
class TabRadio(Tab):

    tabName = "RADIO"
    subMenus = []

    def draw(self):
        pass
    def drawFooter(self, character):
        pass