import pygame, config_new as config
import classes.VaultDweller as VaultDweller
from classes.render.effects import Effects
from abc import ABCMeta, abstractmethod

class Tab(metaclass=ABCMeta):

    selectedSubmenu = 0
    footerSize = (config.WIDTH*0.9, config.MEDcharHeight)
    menu = None
    changed = False
    submenu_surface = None
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
            self.changed = True
        else:
            print("Tried to select a non-valid SubMenu")

    def next_sub(self):
        if self.selectedSubmenu < len(self.subMenus)-1:
            self.selectedSubmenu += 1
        elif self.selectedSubmenu == len(self.subMenus)-1:
            self.selectedSubmenu = 0
        self.changed = True

    def prev_sub(self):
        if self.selectedSubmenu > 0:
            self.selectedSubmenu -= 1
        elif self.selectedSubmenu == 0:
            self.selectedSubmenu = len(self.subMenus)-1
        self.changed = True

    def draw_submenus(self):
        if not self.changed and self.submenu_surface:
            return self.submenu_surface
        self.submenu_surface = pygame.Surface((config.WIDTH, (config.HEIGHT*0.15)))

        spacing = 0
        index = 0
        cicle_menus = []
        for i in range(self.selectedSubmenu, len(self.subMenus)):
            cicle_menus.append(i)
        for i in range(0, self.selectedSubmenu):
            cicle_menus.append(i)
        for index in cicle_menus:
            if index == self.selectedSubmenu:
                color = (255, 255, 255)
            else:
                color = (80, 80, 80)
            text = config.FONT_LRG.render(self.subMenus[index], False, color)
            self.submenu_surface.blit(text, (
                spacing, 0
            ))
            spacing += text.get_width()+config.MEDcharWidth

        self.changed = False
        return self.submenu_surface

    @abstractmethod
    def draw(self):
        return pygame.Surface((config.WIDTH, (config.HEIGHT*0.75)-config.MEDcharHeight))

    @abstractmethod
    def drawFooter(self):
        return pygame.Surface(self.footerSize)

class TabStat(Tab):

    tabName = "STAT"
    subMenus = ["STATUS", "SPECIAL", "PERKS"]
    

    def drawStatus(self, character:VaultDweller):
        img = super().draw()
        body = character.getBodyImage()
        
        head = character.getHeadImage()

        scale = 0.35
        body = pygame.transform.scale(
            body, (int(body.get_width()*scale), int(body.get_height()*scale))
            )
        scale = 0.175
        head = pygame.transform.scale(
            head, (int(head.get_width()*scale), int(head.get_height()*scale))
            )

        rect = img.get_rect()
        body_pos = img.blit(body, (
            rect.centerx - (body.get_width()/2),
            rect.centery - (body.get_height()/2)
        ))

        head_pos = img.blit(head, (
            rect.centerx - (head.get_width()/2),
            rect.centery - body.get_height() + (head.get_height()*0.175)
        ))

        head_bar = head_pos
        head_bar.height = config.SMLcharHeight/2
        head_bar.y -= config.SMLcharHeight
        head_bar.width *= 0.8
        head_bar.x = rect.centerx - (head_bar.width/2)

        bar_height = head_bar.height
        bar_width = head_bar.width

        Effects.draw_progressbar(img, head_bar, character.bodypartsCond['H'], 100)

        Effects.draw_progressbar(img, pygame.Rect(
            body_pos.x-(bar_width*1.5),
            body_pos.y,
            bar_width, bar_height
        ), character.bodypartsCond['LA'], 100)

        Effects.draw_progressbar(img, pygame.Rect(
            body_pos.x+(bar_width*3),
            body_pos.y,
            bar_width, bar_height
        ), character.bodypartsCond['RL'], 100)

        Effects.draw_progressbar(img, pygame.Rect(
            body_pos.x-(bar_width*1.5),
            body_pos.y+(body.get_height()*0.75),
            bar_width, bar_height
        ), character.bodypartsCond['LL'], 100)

        Effects.draw_progressbar(img, pygame.Rect(
            body_pos.x+(bar_width*3),
            body_pos.y+(body.get_height()*0.75),
            bar_width, bar_height
        ), character.bodypartsCond['RA'], 100)

        Effects.draw_progressbar(img, pygame.Rect(
            rect.centerx - (head_bar.width/2),
            body_pos.y + body.get_height()+bar_height,
            bar_width, bar_height
        ), character.health, character.healthMax)

        max_size =rect.height*0.18
        top_padding = rect.height*0.81
        weapon = character.getEquipedWeapon()

        apparels = character.getEquipedApparels()
        resistences = [0, 0, 0]
        res_images = [
            config.IMAGES['status_page']['damage'],
            config.IMAGES['status_page']['electric'],
            config.IMAGES['status_page']['radiation'],
        ]
        for apparel in apparels:
            resistences[0] += apparel.damageResistence
            resistences[1] += apparel.eletricResistence
            resistences[2] += apparel.radiationResistence

        armor_rect = pygame.draw.rect(img, (40, 40, 40), (rect.centerx - (max_size/2), top_padding, max_size, max_size))


        index = 1
        for res in resistences:
            res_rect = pygame.draw.rect(img, (40, 40, 40),(
                rect.centerx + (max_size*(0.5*index)) + config.SMLcharWidth*(0.5*index),
                top_padding,
                max_size/2, max_size)
            )
            icon = Effects.aspect_scale(res_images[index-1], max_size/2.5, max_size/2.5)
            img.blit(icon, (res_rect.centerx - (icon.get_width()/2), res_rect.centery - max_size/3))

            index += 1
            text_res = config.FONT_MED.render(str(res), True, (255, 255, 255))
            img.blit(text_res, (res_rect.centerx-(text_res.get_width()*0.5), res_rect.centery+max_size/15))

        #img.fill((255, 255, 255), (0,img.get_height()*0.8, img.get_width(), img.get_height()*0.2))
        return img

    def draw(self, character: VaultDweller):
        if self.selectedSubmenu == 0:
            if not self.menu or character.changed:
                self.menu = self.drawStatus(character)
        return self.menu

    def drawFooter(self, character:VaultDweller):
        img = super().drawFooter()
        color = (40, 40, 40)
        width_slice = img.get_width()/4
        #draw Boxes
        pygame.draw.rect(img, color, (
            0, 0, width_slice-(config.SMLcharWidth/2), img.get_height()
        ), 0)
        pygame.draw.rect(img, color, (
            width_slice+(config.SMLcharWidth/2), 0,
            (width_slice*2)-(config.SMLcharWidth/2), img.get_height()
        ), 0)
        pygame.draw.rect(img, color, (
            (width_slice*3)+(config.SMLcharWidth), 0,
            img.get_width(), img.get_height()
        ), 0)
        white = (255, 255, 255)
        #draw Texts
        hp_text = config.FONT_MED.render(
            "HP {}/{}".format(character.health, character.healthMax),
            False, white)

        level_text = config.FONT_MED.render("LEVEL {}".format(character.level), False, white)

        ap_text = config.FONT_MED.render(
            "AP {}/{}".format(character.ap, character.apMax),
            False, white)

        img.blit(hp_text, (config.SMLcharWidth, 0))
        img.blit(level_text, (width_slice+(config.SMLcharWidth*1.5), 0))
        img.blit(ap_text, (img.get_width()-config.SMLcharWidth-ap_text.get_width(), 0))

        #draw XP bar
        bar_rect = pygame.Rect(
            level_text.get_width() + width_slice+(config.MEDcharWidth*2),
            level_text.get_width()/10,
            (width_slice*2)-(config.SMLcharWidth/2)-level_text.get_width()-(config.MEDcharWidth*3),
            level_text.get_width()/5
            )

        Effects.draw_progressbar(img, bar_rect, character.exp, character.expMax)

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

    tabName = "MAP"
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