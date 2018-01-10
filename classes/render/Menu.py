# RasPipBoy: A Pip-Boy 3000 implementation for Raspberry Pi
#    Neal D Corbett, 2013
# Screen header/footer
# TODO CONVERT TO FALLOUT4

import pygame
import config_new as config

class Menu:

    size_header_x = config.WIDTH*0.9
    size_header_y = config.HEIGHT*0.15
    old_tab = -1
    
    def __init__(self):
        self.header = pygame.Surface((self.size_header_x, self.size_header_y))

    #Generate The tabs menu on the top
    def draw_header(self, current_tab, tabs):
        if (self.old_tab == current_tab):
            return self.header
        self.old_tab = current_tab
        self.header = pygame.Surface((self.size_header_x, self.size_header_y))

        len_tab = len(tabs)

        SpacingX = (self.size_header_x/len_tab) *0.8
        lines = [(0, self.size_header_y-(config.charHeight/2)), (0, self.size_header_y-config.charHeight)]

        # Draw mode-names, with box around selected one
        for tabNum in range(0, len_tab):
            textImg = config.FONT_LRG.render(tabs[tabNum].tabName, False, config.DRAWCOLOUR)
            TextWidth = (textImg.get_width())
            topPad = self.size_header_y-textImg.get_height()*1.5
            TextX = ((SpacingX*tabNum) + (TextWidth / len_tab-1)) + SpacingX*0.5
            textPos = (TextX, topPad)
            if (tabNum == current_tab):
                lines.append((TextX-config.charWidth,self.size_header_y-config.charHeight))
                lines.append((TextX-config.charWidth,topPad+config.LRGcharHeight/2))
                lines.append((TextX+TextWidth+config.charWidth,topPad+config.LRGcharHeight/2))
                lines.append((TextX+TextWidth+config.charWidth,self.size_header_y-config.charHeight))
                lines.append((self.size_header_x-2, self.size_header_y-config.charHeight))
                lines.append((self.size_header_x-2, self.size_header_y-(config.charHeight/2)))
                pygame.draw.lines(self.header, config.DRAWCOLOUR, False, lines, 1)
                pygame.draw.rect(self.header, (80,0,0), [
                    TextX-2, topPad,
                    TextWidth+4, textImg.get_height()*5,
                ],0)

                # pygame.draw.lines(img, pygame.Color (255, 255, 255), False, [
                # ((TextCentreX - (TextWidth/2)-4),  topLine),
                # ((TextCentreX + (TextWidth/2)+4) , topLine),
                # ], 2)
            self.header.blit(textImg, textPos)
        return self.header

# Generates footer-image:
# def genFooterImgs(ModeNames):

#     footerImgs = []
#     sizeModes = len(ModeNames)
#     print (ModeNames)
#     for thisModeNum in range(0,sizeModes):
#         img = pygame.Surface((config.WIDTH*0.9, config.MEDcharHeight))
#         footerImgs.append(img)
#         # img.fill((255,0,0))

#         TextXPadding = (config.charHeight * 1)
#         TextCentreDiff = ((config.WIDTH - (TextXPadding * 2)) / 5)
#         TextCentreX = TextXPadding + (TextCentreDiff / 2)
#         TextY = (config.HEIGHT - config.charHeight - 4)

#         # Draw lines:
#         topPad = config.HEIGHT/8
#         topLine = config.HEIGHT/6
#         rgtPad = config.WIDTH - cornerPadding

#         # pygame.draw.rect(img, pygame.Color (80, 80, 0), (0, 0, img.get_width(), img.get_height() ), 0)
#         listModes = []
#         for ModeNum in range(thisModeNum, sizeModes):
#             listModes.append(ModeNum)
#         for ModeNum in range(0, thisModeNum):
#             listModes.append(ModeNum)
#         posX = config.MEDcharWidth
#         # Draw mode-names, with box around selected one
#         modifier = 1.0
#         for ModeNum in listModes:
            
#             doSelBox = (ModeNum == thisModeNum)
#             thisText = ModeNames[ModeNum]
#             print (thisText)
#             textColor = (255*modifier, 255*modifier, 255*modifier)
#             textImg = config.FONT_MED.render(thisText, True, textColor)
#             img.blit(textImg, (posX, 0))
#             posX += textImg.get_width() + config.MEDcharWidth
#             modifier -= 0.25

#     return footerImgs
