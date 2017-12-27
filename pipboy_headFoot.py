# RasPipBoy: A Pip-Boy 3000 implementation for Raspberry Pi
#    Neal D Corbett, 2013
# Screen header/footer
# TODO CONVERT TO FALLOUT4

import pygame
import config, main

cornerPadding = 10

class Header:
    
    headerStrings = []
    
    def __init__(self, *args, **kwargs):
        self.parent = args[0]
        self.rootParent = self.parent.rootParent
        self.canvas = pygame.Surface((config.WIDTH, config.HEIGHT))
    
    def drawHeader(self):
        # self.canvas.fill((0,0,0))
        # headerStrings = self.headerStrings

        # # Draw lines:
        # lineDn = (cornerPadding + (config.charHeight * 1.6))
        # midLineDn = (cornerPadding + (config.charHeight * 1.2))
        # lineX = config.WIDTH - cornerPadding
        
        # HalfCharHeight = (config.charHeight / 2)
        # TitleTextY = (cornerPadding - HalfCharHeight)
        # TextPad = ((lineDn - cornerPadding) / 2) - HalfCharHeight
        # UnderTextY = cornerPadding + TextPad

        # # Draw header-text list in reverse order, from right to left:
        # rightIdx = (len(headerStrings)-1)
        # for n in range(rightIdx,-1,-1):
            
        #     thisText = headerStrings[n]
        #     textImg = config.FONT_LRG.render(thisText, True, config.DRAWCOLOUR)
            
        #     TextWidth = (textImg.get_width())
        #     TextHeight = (textImg.get_height())
        #     TextX, TextY = 0, 0
            
        #     if (n == 0):
        #         TextX = lineDn
        #         TextY = TitleTextY
                
        #         TextRect = (TextX - 2, TextY - 2, TextWidth + 4, config.charHeight + 4)
        #         pygame.draw.rect(self.canvas, (0,0,0), TextRect, 0)
        #     else:
        #         TextX = (lineX - TextPad - TextWidth)
        #         TextY = UnderTextY
                
        #         thisLineDn = midLineDn
        #         if (n == rightIdx):
        #             thisLineDn = lineDn
                
        #         if (n == 1):
        #             pygame.draw.lines(self.canvas, config.DRAWCOLOUR, False, [(lineX, thisLineDn), (lineX, cornerPadding), (cornerPadding, cornerPadding), (cornerPadding, lineDn), ], 2)
        #         else:
        #             lineLeft = (TextX - TextPad)
        #             pygame.draw.lines(self.canvas, config.DRAWCOLOUR, False, [(lineX, thisLineDn), (lineX, cornerPadding), (lineLeft, cornerPadding)], 2)

        #     self.canvas.blit(textImg, (TextX, TextY))
            
        #     lineX = (lineLeft - 6)
        return self.canvas
        
    def getHeader(self):
        
        newHeaderStrings = self.parent.getHeaderText()
        changed = (newHeaderStrings != self.headerStrings)
        
        # Only redraw header if text has changed:
        if (changed):
            self.headerStrings = newHeaderStrings
            self.drawHeader()
        
        return self.canvas, changed
#Generate The tabs menu
def genHeaderTabs(tabs, currentTab):
    SizeX = config.WIDTH*0.9
    SizeY = config.HEIGHT*0.15

    img = pygame.Surface((config.WIDTH*0.9, config.HEIGHT*0.15))
    SizeLen = len(tabs)

    SpacingX = SizeX/SizeLen
    lines = [(0, SizeY), (0, SizeY-config.charHeight)]
    
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
            lines.append((SizeX-2, SizeY))
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

    for thisModeNum in range(0,len(ModeNames)):
        img = pygame.Surface((config.WIDTH, config.HEIGHT))
        footerImgs.append(img)
        
        TextXPadding = (config.charHeight * 1)
        TextCentreDiff = ((config.WIDTH - (TextXPadding * 2)) / 5)
        TextCentreX = TextXPadding + (TextCentreDiff / 2)
        TextY = (config.HEIGHT - config.charHeight - 4)
        
        # Draw lines:
        topPad = config.HEIGHT/8
        topLine = config.HEIGHT/6
        rgtPad = config.WIDTH - cornerPadding
        
        # pygame.draw.lines(img, config.DRAWCOLOUR, False, [
        #     (cornerPadding, topLine),
        #     (rgtPad, topLine),
        #     ], 2)
        
        # Draw mode-names, with box around selected one
        # for ModeNum in range(0,5):
            
            # doSelBox = (ModeNum == thisModeNum)
            # BoxColour = (0,0,0)
            
            # thisText = ModeNames[ModeNum]
            #print thisText
            
            # textImg = config.FONT_LRG.render(thisText, True, config.DRAWCOLOUR)
            
            # TextWidth = (textImg.get_width())
            # TextX = (TextCentreX - (TextWidth / 2))
            # textPos = (TextX, topPad)
            #BoxColour
            # pygame.draw.rect(img, pygame.Color (80, 80, 0), (
            #             TextX-4,
            #             topPad,
            #             TextWidth+8,
            #             config.charHeight
            #         ), 0)

            # if (not doSelBox):
            #     pygame.draw.lines(img, pygame.Color (255, 255, 255), False, [
            #     ((TextCentreX - (TextWidth/2)-4),  topLine),
            #     ((TextCentreX + (TextWidth/2)+4) , topLine),
            #     ], 2)
            # img.blit(textImg, textPos)
            
            # TextCentreX += TextCentreDiff
        
    return footerImgs
