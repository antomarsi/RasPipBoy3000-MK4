import pygame, settings, random

class Sounds(object):

    @staticmethod
    def random_up_play():
        random.choice(settings.SOUNDS['UP']).play()

    @staticmethod
    def loop_play():
        humSound = settings.SOUNDS["LOOP"]
        humSound.play(loops=-1)

    @staticmethod
    def play_vertical():
        random.choice(settings.SOUNDS['ROTARY_VERTICAL']).play()

    def play_horizontal():
        random.choice(settings.SOUNDS['ROTARY_HORIZONTAL']).play()
