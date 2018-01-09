import pygame, config_new as config
import classes.VaultDweller as VaultDweller
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
        return pygame.Surface((config.WIDTH, (config.HEIGHT*0.85)-config.MEDcharHeight))

    @abstractmethod
    def drawFooter(self):
        return pygame.Surface(self.footerSize)

class TabStat(Tab):

    tabName = "STAT"
    subMenus = ["STATUS", ""]

    def drawStatus(self, character:VaultDweller):
        img = super().draw()
        body = character.getBodyImage()
        head = character.getHeadImage()

        scale = 0.4
        body = pygame.transform.scale(body, (int(body.get_width()*scale), int(body.get_height()*scale)))
        scale = 0.2
        head = pygame.transform.scale(head, (int(head.get_width()*scale), int(head.get_height()*scale)))

        rect = img.get_rect()
        img.blit(body, (
            rect.centerx - (body.get_width()/2),
            rect.centery - (body.get_height()/2)
        ))
        img.blit(head, (
            rect.centerx - (head.get_width()/2),
            rect.centery - body.get_height() + (head.get_height()*0.175)
        ))
        return img

    def draw(self, character:VaultDweller):
        
        if (self.selectedSubmenu == 0):
            return self.drawStatus(character)
        pass

    def drawFooter(self, character:VaultDweller):
        img = super().drawFooter()
        color = (40, 40, 40)
        width_slice = img.get_width()/4
        #draw Boxes
        pygame.draw.rect(img, color, (0, 0, width_slice-(config.SMLcharWidth/2), img.get_height() ), 0)
        pygame.draw.rect(img, color, (width_slice+(config.SMLcharWidth/2), 0, (width_slice*2)-(config.SMLcharWidth/2), img.get_height() ), 0)
        pygame.draw.rect(img, color, ((width_slice*3)+(config.SMLcharWidth), 0, img.get_width(), img.get_height() ), 0)
        white = (255,255,255)
        #draw Texts
        hp_text = config.FONT_MED.render("HP {}/{}".format(character.health, character.healthMax), True, white)
        level_text = config.FONT_MED.render("LEVEL {}".format(character.level), True, white)
        ap_text = config.FONT_MED.render("AP {}/{}".format(character.ap, character.apMax),True, white)

        img.blit(hp_text, (config.SMLcharWidth, 0))
        img.blit(level_text, (width_slice+(config.SMLcharWidth*1.5), 0))
        img.blit(ap_text, (img.get_width()-config.SMLcharWidth-ap_text.get_width(), 0))

        #draw XP bar

        pygame.draw.rect(img, white,(
                    level_text.get_width() + width_slice+(config.MEDcharWidth*2),
                    level_text.get_width()/10,
                    ((width_slice*2)-(config.SMLcharWidth/2) - level_text.get_width() - (config.MEDcharWidth*3)) * (character.exp/character.expMax),
                    level_text.get_width()/5
                ))
    
        pygame.draw.rect(img, white,(
                    level_text.get_width() + width_slice+(config.MEDcharWidth*2),
                    level_text.get_width()/10,
                    (width_slice*2)-(config.SMLcharWidth/2) - level_text.get_width() - (config.MEDcharWidth*3),
                    level_text.get_width()/5
                ), 1)

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