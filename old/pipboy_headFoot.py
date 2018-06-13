# RasPipBoy: A Pip-Boy 3000 implementation for Raspberry Pi
#    Neal D Corbett, 2013
# Screen header/footer

import pygame, config, main

cornerPadding = 10

class TopMenu:
    
    headerStrings = []
    
    def __init__(self, *args, **kwargs):
        self.parent = args[0]
        self.rootParent = self.parent.rootParent
        self.canvas = pygame.Surface((config.WIDTH, config.HEIGHT))
        
    def getMenu(self):
        
        newHeaderStrings = self.parent.getHeaderText()
        changed = (newHeaderStrings != self.headerStrings)
        
        # Only redraw header if text has changed:
        if (changed):
            footer = pygame.Surface((config.WIDTH-(config.charWidth*2), config.MEDcharHeight))
            footer.fill((0, 0, 0))

            self.canvas.blit(self.parent.drawFooter(footer), (config.charWidth, config.HEIGHT-config.MEDcharHeight*1.5))

        return self.canvas, changed
#Generate The tabs menu
def genHeaderTabs(tabs, currentTab):
    SizeX = config.WIDTH*0.9
    SizeY = config.HEIGHT*0.15

    img = pygame.Surface((config.WIDTH*0.9, config.HEIGHT*0.15))
    SizeLen = len(tabs)

    SpacingX = SizeX/SizeLen
    lines = [(0, SizeY-(config.charHeight/2)), (0, SizeY-config.charHeight)]
    
    lines
    BoxColour = (80,0,0)
    
    # Draw mode-names, with box around selected one
    for tabNum in range(0, SizeLen):
        doSelBox = (tabs[tabNum] == currentTab)

        thisText = tabs[tabNum].name
        #print (thisText)

        textImg = config.FONT_LRG.render(thisText, True, config.DRAWCOLOUR)
        TextWidth = (textImg.get_width())
        topPad = SizeY-textImg.get_height()*1.5
        TextX = ((SpacingX*tabNum) + (TextWidth / 2))
        textPos = (TextX, topPad)

        if (doSelBox):
            lines.append((TextX-config.charWidth,SizeY-config.charHeight))
            lines.append((TextX-config.charWidth,topPad+config.LRGcharHeight/2))
            lines.append((TextX+TextWidth+config.charWidth,topPad+config.LRGcharHeight/2))
            lines.append((TextX+TextWidth+config.charWidth,SizeY-config.charHeight))
            lines.append((SizeX-2, SizeY-config.charHeight))
            lines.append((SizeX-2, SizeY-(config.charHeight/2)))
            pygame.draw.lines(img, config.DRAWCOLOUR, False, lines, 1)
            pygame.draw.rect(img, BoxColour, [
                TextX-2, topPad,
                TextWidth+4, textImg.get_height()*5,
            ],0)
            
            
            # pygame.draw.lines(img, pygame.Color (255, 255, 255), False, [
            # ((TextCentreX - (TextWidth/2)-4),  topLine),
            # ((TextCentreX + (TextWidth/2)+4) , topLine),
            # ], 2)
        img.blit(textImg, textPos)
    return img

# Generates footer-image:
def genFooterImgs(ModeNames):

    footerImgs = []
    sizeModes = len(ModeNames)
    print (ModeNames)
    for thisModeNum in range(0,sizeModes):
        img = pygame.Surface((config.WIDTH*0.9, config.MEDcharHeight))
        footerImgs.append(img)
        # img.fill((255,0,0))

        TextXPadding = (config.charHeight * 1)
        TextCentreDiff = ((config.WIDTH - (TextXPadding * 2)) / 5)
        TextCentreX = TextXPadding + (TextCentreDiff / 2)
        TextY = (config.HEIGHT - config.charHeight - 4)

        # Draw lines:
        topPad = config.HEIGHT/8
        topLine = config.HEIGHT/6
        rgtPad = config.WIDTH - cornerPadding

        # pygame.draw.rect(img, pygame.Color (80, 80, 0), (0, 0, img.get_width(), img.get_height() ), 0)
        listModes = []
        for ModeNum in range(thisModeNum, sizeModes):
            listModes.append(ModeNum)
        for ModeNum in range(0, thisModeNum):
            listModes.append(ModeNum)
        posX = config.MEDcharWidth
        # Draw mode-names, with box around selected one
        modifier = 1.0
        for ModeNum in listModes:
            
            doSelBox = (ModeNum == thisModeNum)
            thisText = ModeNames[ModeNum]
            print (thisText)
            textColor = (255*modifier, 255*modifier, 255*modifier)
            textImg = config.FONT_MED.render(thisText, True, textColor)
            img.blit(textImg, (posX, 0))
            posX += textImg.get_width() + config.MEDcharWidth
            modifier -= 0.25

    return footerImgs
