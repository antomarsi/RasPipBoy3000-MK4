#!/usr/bin/env python
# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame.image
import numpy as np
import os

# IMPORT OBJECT LOADER
from objloader import *


pygame.init()
viewport = (720,720)
hx = viewport[0]/2
hy = viewport[1]/2
display = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF | BLEND_RGBA_ADD )
pygame.display.init()
info = pygame.display.Info()

#Change these
ambient = 0.5 #Ambient lighting
green = 128 #Amount of green hue (adjust if no textures)
flip = False #Alter if text is backwards
swapyz = True #Alter to change up direction
zpos = 50

glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (ambient, ambient, ambient, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

# LOAD OBJECT AFTER PYGAME INIT

path = sys.argv[1]
if os.path.isdir(path):
    for filename in sorted(os.listdir(path)):
        if filename.endswith(".obj"):
            object_file = path + filename
else:
    print("plese provide a folder with a obj file inside")
    sys.exit()

obj = OBJ(object_file, swapyz)
obj.generate()

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(30.0, width/float(height), 1, 2000.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

rx, ry = (0,0)
tx, ty = (0,0)

rotate = move = False
angle = 15
frame = 0
output = False


image_alpha = pygame.Surface((720,720), pygame.SRCALPHA)  # Creates an empty per-pixel alpha Surface.


def greyscale(surface: pygame.Surface):
    arr = pygame.surfarray.pixels3d(surface)
    mean_arr = np.dot(arr[:,:,:], [0.216, 0.587, 0.144])
    mean_arr3d = mean_arr[..., np.newaxis]
    new_arr = np.repeat(mean_arr3d[:, :, :], 3, axis=2)
    return pygame.surfarray.make_surface(new_arr)

def colorize(image, newColor):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param newColor: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy()

    # zero out RGB values
    #image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_MULT)

    return image



while 1:
    clock.tick(30)

    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_LEFT:
            frame = 0
            rx = 360
            output = "left"
        elif e.type == KEYDOWN and e.key == K_RIGHT:
            frame = 0
            rx = 0
            output = "right"
        elif e.type == KEYDOWN and e.key == K_UP:
            flip = True
            print("Flipping the image")
        elif e.type == KEYDOWN and e.key == K_DOWN:
            flip = False
            print("Restoring the image")
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: zpos = max(1, zpos-1)
            elif e.button == 5: zpos += 1
            elif e.button == 1: rotate = True
            elif e.button == 3: move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: rotate = False
            if e.button == 3: move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # RENDER OBJECT
    glTranslate(tx/20., ty/20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    obj.render()

    buffer = glReadPixels(0, 0, *viewport, GL_RGBA, GL_UNSIGNED_BYTE) #Convert the OpenGL surface to a regular surface

    image = pygame.image.fromstring(buffer, viewport, "RGBA") #Get the Open GL buffer
    image = pygame.transform.flip(image,flip,True) #Flip the image

    image = greyscale(image) #Greyscale the image
    image.set_colorkey((0,0,0)) #Set black to transparent

    #image_alpha.fill((0,0,0,0)) #Clear last image
    #image_alpha.blit(image,(0,0)) #Blit to convert black to transparency

    image_colorized = colorize(image,(0,green,0)) # Colorize the image

    pygame.display.flip()


    if output == "right":
        if rx <= 360-angle:
            scaled = pygame.transform.smoothscale(image_colorized,(240,240)) #Shrink to output
            pygame.image.save_extended(scaled, path + "%03d" % frame + ".png") #Save as a file
            rx += angle
            frame += 1
        else:
            frame = 0
            output = False

    if output == "left":
        if rx >= 0+angle:
            scaled = pygame.transform.smoothscale(image_colorized,(240,240)) #Shrink to output
            pygame.image.save_extended(scaled, path + "%03d" % frame + ".png") #Save as a file
            rx -= angle
            frame += 1
        else:
            frame = 0
            output = False
