import pygame
from pygame.locals import *


class App(object):
    def __init__(self):
        self.screen
    topleft = (0, 0)


class Scanline():
    def __init__(self, skip, speed, width, height, color):
        self.line = 0
        self.offset = 0
        self.skip = skip
        self.speed = speed
        self.height = height
        self.width = width
        self.color = color
        self.line_surface = pygame.Surface((width, height))
        self.line_surface.convert_alpha()
        self.line_surface.set_colorkey((0, 0, 0))

    def update(self, dt):
        self.line_surface.fill((0, 0, 0))
        for _ in range(self.speed):
            pygame.draw.line(self.line_surface, self.color,
                             (0, self.line), (self.width, self.line), 1)
            self.line += self.skip * dt
            if self.line > self.height:
                self.offset += 1
                self.line = self.offset
            if self.offset == self.skip:
                self.offset = 0
        # pygame.draw.line(self.line_surface,self.color,line[0],line[1],1)
        return self.line_surface


def blurSurf(surface, amt):
    """
    Blur the given surface by the given 'amount'.  Only values 1 and greater
    are valid.  Value 1 = no blur.
    """
    if amt < 1.0:
        raise ValueError(
            "Arg 'amt' must be greater than 1.0, passed in value is %s" % amt)
    scale = 1.0/float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0]*scale), int(surf_size[1]*scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf


DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_BORDER_THICKNESS = 100
DEFAULT_BOUNDS = {'left': 80, 'top': 50, 'right': 80, 'bottom': 65}
DEFAULT_SCANLINE_COLOR = (24, 130, 24)
DEFAULT_SCANLINE_SKIP = 2
DEFAULT_SCANLINE_SPEED = 2
DEFAULT_FRAMERATE = 23

width = DEFAULT_WIDTH
height = DEFAULT_HEIGHT
border_thickness = None  # Calculated value.
fullscreen = False
scanlineColor = DEFAULT_SCANLINE_COLOR
scanlineSkip = DEFAULT_SCANLINE_SKIP
scanlineSpeed = DEFAULT_SCANLINE_SPEED

# Defaults for asset fallbacks
FALLBACK_BACKGROUND_COLOR = (24, 30, 24, 32)
FALLBACK_FOREGROUND_COLOR = (1, 1, 1)
FALLBACK_ICON_COLOR = (1, 1, 1)
framerate = DEFAULT_FRAMERATE

pygame.init()

clock = pygame.time.Clock()
BLACK = (0, 0, 0)

# Pygame Initialization
mode_flags = 0
if fullscreen:
    mode_flags |= pygame.FULLSCREEN
screen = pygame.display.set_mode((width, height), mode_flags)

scanlines = Scanline(scanlineSkip, scanlineSpeed, width, height, scanlineColor)
running = 1
while(running):
    if (running == 1):
        # --------------------------
        # Render Background
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, BLACK, [0, 0, width, height])
        # --------------------------
        # Scanline
        screen.blit(scanlines.update(), topleft)
        # --------------------------
        pygame.draw.rect(screen, (0, 255, 0), [150, 10, 50, 20])

        # States
        # ----Menu and Text State
        screen.blit(blurSurf(screen, 3), topleft)
        pygame.display.flip()
        # --------------------------
        # Frame Control
        clock.tick(framerate)
    else:
        pygame.time.wait(500)
pygame.quit()

try:
    sys.exit("Good night")
except SystemExit:
    # Cleanup
    print("Good night")
