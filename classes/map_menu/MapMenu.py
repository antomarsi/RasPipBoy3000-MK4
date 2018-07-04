import os, abc, pygame, settings
from classes.interface.TabMenuInterface import TabMenuInterface

class DataMenu(TabMenuInterface):

    name = 'Map'
    surface = None
    places = []

    saveVersion = 1

    #User-view's Zoom/Position
    viewZoom = 1.0
    viewPosX = 0.0
    viewPosY = 0.0

    cursorRadius = 32
    cursorPosX = 0.0
    cursorPosY = 0.0

    mapType = 0
    mapImage = 0
    mapSize = 640
    mapScale = 2

    cursorSize = 16
    markerSizeSm = 32
    markerSizeBg = 48
    halfMarkerSizeSm = markerSizeSm/2
    halfMarkerSizeBg = markerSizeBg/2

    #used to implement mouse-acceleration:
    moveStartTick 0
    lastMoveTick = 0

    mapImageSize = (mapSize * mapScale)


    def __init__(self):
        print('Initialize tab Menu')
        self.size = (int(os.getenv('SCREEN_WIDTH')), int(int(os.getenv('SCREEN_HEIGHT'))*0.9))
        self.surface = pygame.Surface(self.size)
        print('Generating cursor', end='')
        self.generate_cursor()
        print('(done)')
        print('(done)')


    def generate_cursor(self):
       # Generate cursor-box image:
        cursBoxSize = (2 * self.cursorRadius)
        thirdSize = (cursBoxSize / 3)
        self.cursorBox = pygame.Surface((cursBoxSize, cursBoxSize))
        self.cursorBox.fill((0,0,0))
        lnSize = 2
        pygame.draw.rect(self.cursorBox, (255,255,255), (self.cursorRadius-(lnSize/2),self.cursorRadius-(lnSize/2),lnSize,lnSize), 0)
        pygame.draw.lines(self.cursorBox, (255,255,255), False, [
            (lnSize,thirdSize),
            (lnSize,lnSize),
            (thirdSize,lnSize)
        ], lnSize)
        pygame.draw.lines(self.cursorBox, (255,255,255), False, [
            (cursBoxSize-thirdSize,lnSize),
            (cursBoxSize-lnSize,lnSize),
            (cursBoxSize-lnSize,thirdSize)
        ], lnSize)
        pygame.draw.lines(self.cursorBox, (255,255,255), False, [
            (lnSize,cursBoxSize-thirdSize),
            (lnSize,cursBoxSize-lnSize),
            (thirdSize,cursBoxSize-lnSize)
        ], lnSize)
        pygame.draw.lines(self.cursorBox, (255,255,255), False, [
            (cursBoxSize-thirdSize, cursBoxSize-lnSize),
            (cursBoxSize-lnSize, cursBoxSize-lnSize),
            (cursBoxSize-lnSize, cursBoxSize-thirdSize)
        ], lnSize)
        self.cursorBox = self.cursorBox.convert()
        self.resetCursorPos()

    def event(self, event):
        pass

    def process(self):
        pass

    def draw(self):
        self.surface.fill((255,255,255))
        pass
